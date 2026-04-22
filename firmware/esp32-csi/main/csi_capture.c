#include "csi_capture.h"
#include "esp_wifi.h"
#include "esp_log.h"
#include "esp_timer.h"
#include <string.h>

static const char *TAG = "csi_capture";
static csi_packet_callback_t s_callback = NULL;
static char s_sensor_id[32] = {0};

static void csi_callback(void *ctx, wifi_csi_info_t *info) {
    if (!info || !info->buf || !s_callback) return;

    csi_packet_t pkt = {0};
    strncpy(pkt.sensor_id, s_sensor_id, sizeof(pkt.sensor_id) - 1);
    pkt.timestamp_us  = esp_timer_get_time();
    pkt.rssi          = info->rx_ctrl.rssi;
    pkt.noise_floor   = info->rx_ctrl.noise_floor;
    pkt.antenna_count = 1;

    uint8_t n = info->len < CSI_BUFFER_SIZE ? info->len : CSI_BUFFER_SIZE;
    pkt.num_subcarriers = n / 2;
    for (uint8_t i = 0; i < n; i++) {
        pkt.csi_data[i] = (int16_t)info->buf[i];
    }

    s_callback(&pkt);
}

void csi_capture_init(const char *sensor_id, csi_packet_callback_t cb) {
    strncpy(s_sensor_id, sensor_id, sizeof(s_sensor_id) - 1);
    s_callback = cb;

    wifi_csi_config_t csi_cfg = {
        .lltf_en           = true,
        .htltf_en          = true,
        .stbc_htltf2_en    = true,
        .ltf_merge_en      = true,
        .channel_filter_en = true,
        .manu_scale        = false,
    };
    ESP_ERROR_CHECK(esp_wifi_set_csi_config(&csi_cfg));
    ESP_ERROR_CHECK(esp_wifi_set_csi_rx_cb(csi_callback, NULL));
    ESP_ERROR_CHECK(esp_wifi_set_csi(true));
    ESP_LOGI(TAG, "CSI capture started for sensor %s", sensor_id);
}

void csi_capture_stop(void) {
    esp_wifi_set_csi(false);
    s_callback = NULL;
}
