import Foundation

class APIService {
    static let shared = APIService()

    var baseURL: String {
        UserDefaults.standard.string(forKey: "serverURL") ?? "http://localhost:8000"
    }

    func url(_ path: String) -> URL {
        URL(string: baseURL + path)!
    }

    private func authorizedRequest(_ path: String, method: String = "GET") -> URLRequest {
        var request = URLRequest(url: url(path))
        request.httpMethod = method
        if let token = AuthService.shared.token {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        return request
    }

    func fetchSensors() async throws -> [Sensor] {
        let (data, _) = try await URLSession.shared.data(for: authorizedRequest("/api/v1/sensors"))
        return try JSONDecoder().decode([Sensor].self, from: data)
    }

    func fetchSensorHealth(sensorId: String) async throws -> SensorHealth {
        let (data, _) = try await URLSession.shared.data(for: authorizedRequest("/api/v1/sensors/\(sensorId)/health"))
        return try JSONDecoder().decode(SensorHealth.self, from: data)
    }

    func fetchAlerts(acknowledged: Bool = false) async throws -> [AlertItem] {
        let (data, _) = try await URLSession.shared.data(for: authorizedRequest("/api/v1/alerts?acknowledged=\(acknowledged)"))
        return try JSONDecoder().decode([AlertItem].self, from: data)
    }

    func acknowledgeAlert(id: String) async throws {
        let req = authorizedRequest("/api/v1/alerts/\(id)/acknowledge", method: "POST")
        _ = try await URLSession.shared.data(for: req)
    }

    // Sleep endpoints
    func fetchCurrentSleep(sensorId: String) async throws -> SleepSessionInfo {
        let (data, _) = try await URLSession.shared.data(for: authorizedRequest("/api/v1/sleep/current?sensor_id=\(sensorId)"))
        return try JSONDecoder().decode(SleepSessionInfo.self, from: data)
    }

    func fetchTonightSleep(sensorId: String) async throws -> SleepSessionInfo {
        let (data, _) = try await URLSession.shared.data(for: authorizedRequest("/api/v1/sleep/tonight?sensor_id=\(sensorId)"))
        return try JSONDecoder().decode(SleepSessionInfo.self, from: data)
    }

    func fetchSleepHistory(sensorId: String, days: Int = 7) async throws -> [DailySummary] {
        let (data, _) = try await URLSession.shared.data(for: authorizedRequest("/api/v1/sleep/history?sensor_id=\(sensorId)&days=\(days)"))
        return try JSONDecoder().decode([DailySummary].self, from: data)
    }

    func fetchWeeklyTrend(sensorId: String) async throws -> WeeklyTrend {
        let (data, _) = try await URLSession.shared.data(for: authorizedRequest("/api/v1/sleep/weekly?sensor_id=\(sensorId)"))
        return try JSONDecoder().decode(WeeklyTrend.self, from: data)
    }

    // Calibration
    func startCalibration(sensorId: String, phase: String) async throws -> String {
        var req = authorizedRequest("/api/v1/calibration/start", method: "POST")
        req.httpBody = try JSONEncoder().encode(["sensor_id": sensorId, "phase": phase])
        let (data, _) = try await URLSession.shared.data(for: req)
        struct Resp: Codable { let session_id: String }
        return try JSONDecoder().decode(Resp.self, from: data).session_id
    }

    func completeCalibration(sessionId: String) async throws -> CalibrationResult {
        let req = authorizedRequest("/api/v1/calibration/\(sessionId)/complete", method: "POST")
        let (data, _) = try await URLSession.shared.data(for: req)
        return try JSONDecoder().decode(CalibrationResult.self, from: data)
    }
}
