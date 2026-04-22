import Foundation
import Combine

@MainActor
class WebSocketService: ObservableObject {
    static let shared = WebSocketService()

    @Published var latestStatus: RoomStatus?
    @Published var isConnected = false
    @Published var latestEvent: WSEvent?

    private var task: URLSessionWebSocketTask?
    private var reconnectDelay: TimeInterval = 1.0
    private var shouldConnect = false
    private var pingTimer: Timer?

    func connect() {
        shouldConnect = true
        reconnectDelay = 1.0
        openConnection()
    }

    func disconnect() {
        shouldConnect = false
        task?.cancel(with: .normalClosure, reason: nil)
        task = nil
        isConnected = false
        pingTimer?.invalidate()
        pingTimer = nil
    }

    private func openConnection() {
        guard shouldConnect, let token = AuthService.shared.token else { return }
        let baseURL = UserDefaults.standard.string(forKey: "serverURL") ?? "http://localhost:8000"
        let wsURL = baseURL.replacingOccurrences(of: "http://", with: "ws://")
                           .replacingOccurrences(of: "https://", with: "wss://")
        guard let url = URL(string: "\(wsURL)/ws/live?token=\(token)") else { return }

        let session = URLSession(configuration: .default)
        task = session.webSocketTask(with: url)
        task?.resume()
        isConnected = true
        reconnectDelay = 1.0
        schedulePing()
        receiveLoop()
    }

    private func receiveLoop() {
        task?.receive { [weak self] result in
            guard let self = self else { return }
            switch result {
            case .success(let message):
                if case .string(let text) = message {
                    self.handleMessage(text)
                }
                self.receiveLoop()
            case .failure:
                Task { @MainActor in
                    self.handleDisconnect()
                }
            }
        }
    }

    private func handleMessage(_ text: String) {
        guard let data = text.data(using: .utf8) else { return }
        guard let msg = try? JSONDecoder().decode(WSMessage.self, from: data) else { return }
        Task { @MainActor in
            switch msg.type {
            case "status_update":
                self.latestStatus = msg.data
            case "event":
                self.latestEvent = msg.event
            default:
                break
            }
        }
    }

    private func handleDisconnect() {
        isConnected = false
        pingTimer?.invalidate()
        pingTimer = nil
        guard shouldConnect else { return }
        let delay = min(reconnectDelay, 30.0)
        reconnectDelay = min(reconnectDelay * 2, 30.0)
        DispatchQueue.main.asyncAfter(deadline: .now() + delay) { [weak self] in
            self?.openConnection()
        }
    }

    private func schedulePing() {
        pingTimer?.invalidate()
        pingTimer = Timer.scheduledTimer(withTimeInterval: 30.0, repeats: true) { [weak self] _ in
            self?.task?.send(.string("{\"type\":\"ping\"}")) { _ in }
        }
    }
}
