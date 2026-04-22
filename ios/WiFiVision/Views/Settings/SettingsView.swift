import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var auth: AuthService
    @State private var serverURL = UserDefaults.standard.string(forKey: "serverURL") ?? "http://localhost:8000"
    @AppStorage("roomName") private var roomName = "Chambre de bébé"
    @State private var showLogout = false

    var body: some View {
        ZStack {
            LumiColor.background.ignoresSafeArea()
            ScrollView(showsIndicators: false) {
                VStack(spacing: 16) {
                    HStack {
                        Text("Réglages")
                            .font(LumiFont.title)
                            .foregroundStyle(LumiColor.textPrimary)
                        Spacer()
                    }
                    .padding(.horizontal, 24).padding(.top, 8)

                    // Account
                    SettingsSection(title: "Compte") {
                        SettingsRow(icon: "person.circle", label: "Utilisateur", value: auth.username)
                        Divider().background(LumiColor.separator)
                        Button(role: .destructive) { showLogout = true } label: {
                            HStack {
                                Image(systemName: "rectangle.portrait.and.arrow.right")
                                    .foregroundStyle(LumiColor.alert)
                                Text("Se déconnecter").foregroundStyle(LumiColor.alert)
                                Spacer()
                            }
                            .padding(.vertical, 4)
                        }
                    }

                    // Room
                    SettingsSection(title: "Chambre") {
                        HStack {
                            Image(systemName: "house").foregroundStyle(LumiColor.primary)
                            TextField("Nom de la chambre", text: $roomName)
                                .foregroundStyle(LumiColor.textPrimary)
                        }
                        .padding(.vertical, 4)
                    }

                    // Connection
                    SettingsSection(title: "Connexion serveur") {
                        HStack {
                            Image(systemName: "network").foregroundStyle(LumiColor.primary)
                            TextField("URL du serveur", text: $serverURL)
                                .foregroundStyle(LumiColor.textPrimary)
                                .autocorrectionDisabled()
                                .textInputAutocapitalization(.never)
                                .onChange(of: serverURL) { newVal in
                                    UserDefaults.standard.set(newVal, forKey: "serverURL")
                                }
                        }
                        .padding(.vertical, 4)
                    }

                    // About
                    SettingsSection(title: "À propos") {
                        SettingsRow(icon: "info.circle", label: "Version", value: "1.0.0")
                        Divider().background(LumiColor.separator)
                        VStack(alignment: .leading, spacing: 6) {
                            Label("Mentions légales", systemImage: "doc.text")
                                .font(LumiFont.body)
                                .foregroundStyle(LumiColor.textSecondary)
                            Text("LumiBaby est un outil d'information basé sur la détection de mouvement. Il ne constitue pas un dispositif médical et ne garantit pas la sécurité ou la santé de votre bébé.")
                                .font(LumiFont.caption)
                                .foregroundStyle(LumiColor.textSecondary.opacity(0.7))
                        }
                        .padding(.vertical, 4)
                    }
                }
                .padding(.bottom, 32)
            }
        }
        .confirmationDialog("Se déconnecter ?", isPresented: $showLogout) {
            Button("Se déconnecter", role: .destructive) { auth.logout() }
        }
    }
}

private struct SettingsSection<Content: View>: View {
    let title: String
    @ViewBuilder let content: Content

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(title)
                .font(LumiFont.captionBold)
                .foregroundStyle(LumiColor.textSecondary)
                .padding(.horizontal, 24)
            VStack(spacing: 0) { content }
                .padding(.horizontal, 16)
                .padding(.vertical, 14)
                .lumiCard()
                .padding(.horizontal, 20)
        }
    }
}

private struct SettingsRow: View {
    let icon: String
    let label: String
    let value: String

    var body: some View {
        HStack {
            Image(systemName: icon).foregroundStyle(LumiColor.primary)
            Text(label).font(LumiFont.body).foregroundStyle(LumiColor.textPrimary)
            Spacer()
            Text(value).font(LumiFont.body).foregroundStyle(LumiColor.textSecondary)
        }
        .padding(.vertical, 4)
    }
}
