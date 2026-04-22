#pragma once
#include "csi_capture.h"
#include "esp_err.h"

esp_err_t packet_sender_init(const char *server_ip, uint16_t server_port);
void      packet_sender_send(const csi_packet_t *pkt);
void      packet_sender_send_heartbeat(void);
