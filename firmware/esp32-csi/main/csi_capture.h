#pragma once
#include "esp_wifi_types.h"

#define CSI_BUFFER_SIZE   128

typedef struct {
    char    sensor_id[32];
    int64_t timestamp_us;
    int8_t  rssi;
    int8_t  noise_floor;
    int16_t csi_data[CSI_BUFFER_SIZE];
    uint8_t num_subcarriers;
    uint8_t antenna_count;
} csi_packet_t;

typedef void (*csi_packet_callback_t)(const csi_packet_t *pkt);

void csi_capture_init(const char *sensor_id, csi_packet_callback_t cb);
void csi_capture_stop(void);
