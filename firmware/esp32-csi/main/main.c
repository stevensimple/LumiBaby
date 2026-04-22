#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "wifi_manager.h"
#include "csi_capture.h"
#include "packet_sender.h"

static const char *TAG = "main";

/* ── Configuration ── edit these or load from NVS ── */
#define WIFI_SSID        "YourWiFiSSID"
#define WIFI_PASSWORD    "YourWiFiPassword"
#define BACKEND_IP       "192.168.1.100"
#define BACKEND_PORT     8000
#define SENSOR_ID        "esp32_001"
#define HEARTBEAT_INTERVAL_MS  30000

static void on_csi_packet(const csi_packet_t *pkt) {
    packet_sender_send(pkt);
}

static void heartbeat_task(void *arg) {
    while (1) {
        vTaskDelay(pdMS_TO_TICKS(HEARTBEAT_INTERVAL_MS));
        if (wifi_manager_is_connected()) {
            packet_sender_send_heartbeat();
        }
    }
}

void app_main(void) {
    ESP_LOGI(TAG, "WiFiVision node starting — sensor_id: %s", SENSOR_ID);

    if (wifi_manager_init(WIFI_SSID, WIFI_PASSWORD) != ESP_OK) {
        ESP_LOGE(TAG, "WiFi init failed. Rebooting in 5s...");
        vTaskDelay(pdMS_TO_TICKS(5000));
        esp_restart();
    }

    packet_sender_init(BACKEND_IP, BACKEND_PORT);
    csi_capture_init(SENSOR_ID, on_csi_packet);

    xTaskCreate(heartbeat_task, "heartbeat", 2048, NULL, 5, NULL);
    ESP_LOGI(TAG, "CSI streaming active → %s:%d", BACKEND_IP, BACKEND_PORT);
}
