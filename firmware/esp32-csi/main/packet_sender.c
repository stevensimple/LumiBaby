#include "packet_sender.h"
#include "esp_log.h"
#include "esp_http_client.h"
#include "esp_timer.h"
#include <stdio.h>
#include <string.h>

static const char *TAG = "pkt_sender";
static char s_server_url[128] = {0};
static char s_ingest_url[160] = {0};

esp_err_t packet_sender_init(const char *server_ip, uint16_t server_port) {
    snprintf(s_server_url, sizeof(s_server_url), "http://%s:%d", server_ip, server_port);
    snprintf(s_ingest_url, sizeof(s_ingest_url), "%s/api/v1/ingest", s_server_url);
    ESP_LOGI(TAG, "Ingest endpoint: %s", s_ingest_url);
    return ESP_OK;
}

static esp_err_t _http_event_handler(esp_http_client_event_t *evt) {
    return ESP_OK;
}

void packet_sender_send(const csi_packet_t *pkt) {
    char json[2048];
    char csi_array[1024] = "[";
    int  offset = 1;
    for (int i = 0; i < pkt->num_subcarriers * 2 && offset < (int)sizeof(csi_array) - 8; i++) {
        offset += snprintf(csi_array + offset, sizeof(csi_array) - offset - 2,
                           i == 0 ? "%d" : ",%d", pkt->csi_data[i]);
    }
    strncat(csi_array, "]", sizeof(csi_array) - strlen(csi_array) - 1);

    double timestamp_s = (double)pkt->timestamp_us / 1e6;
    snprintf(json, sizeof(json),
             "{\"sensor_id\":\"%s\","
             "\"timestamp\":%.3f,"
             "\"rssi\":%d,"
             "\"noise_floor\":%d,"
             "\"raw_csi\":%s,"
             "\"num_subcarriers\":%d,"
             "\"antenna_count\":%d}",
             pkt->sensor_id, timestamp_s, pkt->rssi, pkt->noise_floor,
             csi_array, pkt->num_subcarriers, pkt->antenna_count);

    esp_http_client_config_t cfg = {
        .url            = s_ingest_url,
        .event_handler  = _http_event_handler,
        .timeout_ms     = 3000,
    };
    esp_http_client_handle_t client = esp_http_client_init(&cfg);
    esp_http_client_set_method(client, HTTP_METHOD_POST);
    esp_http_client_set_header(client, "Content-Type", "application/json");
    esp_http_client_set_post_field(client, json, strlen(json));
    esp_err_t err = esp_http_client_perform(client);
    if (err != ESP_OK) {
        ESP_LOGW(TAG, "Send failed: %s", esp_err_to_name(err));
    }
    esp_http_client_cleanup(client);
}

void packet_sender_send_heartbeat(void) {
    ESP_LOGI(TAG, "Heartbeat OK");
}
