#pragma once
#include "esp_err.h"

#define WIFI_SSID_MAX_LEN     32
#define WIFI_PASS_MAX_LEN     64

esp_err_t wifi_manager_init(const char *ssid, const char *password);
bool      wifi_manager_is_connected(void);
