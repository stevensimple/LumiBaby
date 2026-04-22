import Foundation
import Security

class AuthService: ObservableObject {
    static let shared = AuthService()
    @Published var isAuthenticated = false
    @Published var username: String = ""

    private let tokenKey = "wifivision_token"
    private let usernameKey = "wifivision_username"

    var token: String? {
        get { UserDefaults.standard.string(forKey: tokenKey) }
        set {
            UserDefaults.standard.set(newValue, forKey: tokenKey)
            isAuthenticated = newValue != nil
        }
    }

    init() {
        isAuthenticated = token != nil
        username = UserDefaults.standard.string(forKey: usernameKey) ?? ""
    }

    func login(username: String, password: String) async throws {
        let url = APIService.shared.url("/api/v1/auth/login")
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")
        let body = "username=\(username.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? username)&password=\(password.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? password)"
        request.httpBody = body.data(using: .utf8)
        let (data, response) = try await URLSession.shared.data(for: request)
        guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
            throw URLError(.userAuthenticationRequired)
        }
        struct TokenResponse: Codable { let access_token: String }
        let result = try JSONDecoder().decode(TokenResponse.self, from: data)
        await MainActor.run {
            self.token = result.access_token
            self.username = username
            UserDefaults.standard.set(username, forKey: self.usernameKey)
            self.isAuthenticated = true
        }
    }

    func logout() {
        token = nil
        username = ""
        UserDefaults.standard.removeObject(forKey: usernameKey)
        isAuthenticated = false
    }
}
