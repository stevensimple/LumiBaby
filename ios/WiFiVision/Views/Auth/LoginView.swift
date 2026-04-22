import SwiftUI

struct LoginView: View {
    @EnvironmentObject var auth: AuthService
    @State private var username = ""
    @State private var password = ""
    @State private var isLoading = false
    @State private var error: String?

    var body: some View {
        ZStack {
            LumiColor.background.ignoresSafeArea()
            VStack(spacing: 36) {
                Spacer()
                VStack(spacing: 12) {
                    Image(systemName: "moon.zzz.fill")
                        .font(.system(size: 60))
                        .foregroundStyle(LumiColor.primary)
                    Text("LumiBaby")
                        .font(LumiFont.largeTitle)
                        .foregroundStyle(LumiColor.textPrimary)
                    Text("Surveillance intelligente du sommeil")
                        .font(LumiFont.body)
                        .foregroundStyle(LumiColor.textSecondary)
                        .multilineTextAlignment(.center)
                }
                VStack(spacing: 14) {
                    LumiTextField(placeholder: "Identifiant", text: $username, isSecure: false)
                    LumiTextField(placeholder: "Mot de passe", text: $password, isSecure: true)
                    if let err = error {
                        Text(err)
                            .font(LumiFont.caption)
                            .foregroundStyle(LumiColor.alert)
                    }
                    Button { Task { await login() } } label: {
                        Group {
                            if isLoading {
                                ProgressView().tint(.white)
                            } else {
                                Text("Se connecter").font(LumiFont.headline)
                            }
                        }
                        .foregroundStyle(.white)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 16)
                        .background(LumiColor.primary)
                        .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
                    }
                    .disabled(isLoading || username.isEmpty || password.isEmpty)
                }
                .padding(.horizontal, 28)
                Spacer()
                Text("Sans caméra · Sans intrusion · Respectueux de la vie privée")
                    .font(LumiFont.caption)
                    .foregroundStyle(LumiColor.textSecondary.opacity(0.6))
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 28)
                    .padding(.bottom, 16)
            }
        }
    }

    private func login() async {
        isLoading = true
        error = nil
        do {
            try await auth.login(username: username, password: password)
        } catch {
            self.error = "Identifiants incorrects"
        }
        isLoading = false
    }
}

private struct LumiTextField: View {
    let placeholder: String
    @Binding var text: String
    let isSecure: Bool

    var body: some View {
        Group {
            if isSecure {
                SecureField(placeholder, text: $text)
            } else {
                TextField(placeholder, text: $text)
                    .autocorrectionDisabled()
                    .textInputAutocapitalization(.never)
            }
        }
        .foregroundStyle(Color.white)
        .padding()
        .background(LumiColor.card)
        .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
    }
}
