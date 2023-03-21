""" Copyright start
  Copyright (C) 2008 - 2023 Fortinet Inc.
  All rights reserved.
  FORTINET CONFIDENTIAL & FORTINET PROPRIETARY SOURCE CODE
  Copyright end """

from connectors.core.connector import get_logger, ConnectorError
import requests

logger = get_logger('azure-storage-table')

STORAGE_SERVICE_ENDPOINT = ".table.core.windows.net"


def api_request(method, endpoint, connector_info, config, params=None, data=None, Json=None, verify_ssl=False,
                headers={}):
    try:
        headers['Content-Type'] = 'application/json'
        headers['Accept'] = 'application/json;odata=nometadata'
        response = requests.request(method, endpoint, headers=headers, params=params, json=Json, verify=verify_ssl)
        if response.status_code in [200, 201, 202, 204]:
            if response.status_code == 204:
                return response
            else:
                return response.json()
        else:
            raise ConnectorError("{0}".format(response.content))
    except requests.exceptions.SSLError:
        raise ConnectorError('SSL certificate validation failed')
    except requests.exceptions.ConnectTimeout:
        raise ConnectorError('The request timed out while trying to connect to the server')
    except requests.exceptions.ReadTimeout:
        raise ConnectorError(
            'The server did not send any data in the allotted amount of time')
    except requests.exceptions.ConnectionError:
        raise ConnectorError('Invalid Credentials')
    except Exception as err:
        raise ConnectorError(str(err))


def _check_health(config, connector_info):
    try:
        if query_table(config, {}, connector_info):
            return True
        else:
            raise ConnectorError("Invalid Credentials")
    except Exception as err:
        raise ConnectorError(str(err))


def create_table(config, params, connector_info):
    endpoint = "https://" + config.get("accountName") + STORAGE_SERVICE_ENDPOINT + "/Tables" + config.get("sas_token")
    data = {
        "TableName": params.get("table_name")
    }
    response = api_request("POST", endpoint, connector_info, config, Json=data)
    return response


def delete_table(config, params, connector_info):
    endpoint = "https://" + config.get("accountName") + STORAGE_SERVICE_ENDPOINT + "/Tables" + '(\'' + params.get(
        "table_name") + '\')' + config.get("sas_token")

    response = api_request("DELETE", endpoint, connector_info, config)
    return response


def query_table(config, params, connector_info):
    endpoint = "https://" + config.get("accountName") + STORAGE_SERVICE_ENDPOINT + "/Tables" + config.get("sas_token")
    query_params = {}
    if params.get("query_filter") is not None:
        query_params.update({"$filter": params.get("query_filter")})
    if params.get("records_limit") is not None:
        query_params.update({"$top": params.get("records_limit")})

    response = api_request("GET", endpoint, connector_info, config, params=query_params)
    return response


def insert_entity_table(config, params, connector_info):
    endpoint = "https://" + config.get("accountName") + STORAGE_SERVICE_ENDPOINT + "/" + params.get("table_name") + \
               config.get("sas_token")
    query_params = params.get("entity_fields")
    query_params.update({"PartitionKey": params.get("partition_key")})
    query_params.update({"RowKey": params.get("row_key")})
    response = api_request("POST", endpoint, connector_info, config, Json=query_params)
    return response


def update_entity_table(config, params, connector_info):
    endpoint = "https://" + config.get("accountName") + STORAGE_SERVICE_ENDPOINT + "/" + params.get("table_name")
    query_string = "("
    if params.get("partition_key"):
        query_string += "PartitionKey='" + params.get("partition_key") + "',"
    if params.get("row_key"):
        query_string += "RowKey='" + params.get("row_key") + "'"
    query_string += ")"

    endpoint += query_string + config.get("sas_token")
    response = api_request("PUT", endpoint, connector_info, config, Json=params.get("entity_fields"))
    return response


def query_entity_table(config, params, connector_info):
    endpoint = "https://" + config.get("accountName") + STORAGE_SERVICE_ENDPOINT + "/" + params.get("table_name")
    query_string = "("
    if params.get("partition_key"):
        query_string += "PartitionKey='" + params.get("partition_key") + "',"
    if params.get("row_key"):
        query_string += "RowKey='" + params.get("row_key") + "'"
    query_string += ")"

    endpoint += query_string + config.get("sas_token")
    query_params = {}
    if params.get("property_names"):
        query_params.update({
            "$select": params.get("property_names")
        })
    if params.get("query_filter"):
        query_params.update({
            "$filter": params.get("query_filter")
        })

    response = api_request("GET", endpoint, connector_info, config, params=query_params)
    return response


def delete_entity_table(config, params, connector_info):
    endpoint = "https://" + config.get("accountName") + STORAGE_SERVICE_ENDPOINT + "/" + params.get("table_name")

    query_string = "("
    if params.get("partition_key"):
        query_string += "PartitionKey='" + params.get("partition_key") + "',"
    if params.get("row_key"):
        query_string += "RowKey='" + params.get("row_key") + "'"
    query_string += ")"

    endpoint += query_string + config.get("sas_token")

    headers = {
        "If-Match": "*"
    }
    response = api_request("DELETE", endpoint, connector_info, config, headers=headers)
    return response


operations = {
    'create_table': create_table,
    'delete_table': delete_table,
    'query_table': query_table,
    'insert_entity_table': insert_entity_table,
    'query_entity_table': query_entity_table,
    'update_entity_table': update_entity_table,
    'delete_entity_table': delete_entity_table
}
