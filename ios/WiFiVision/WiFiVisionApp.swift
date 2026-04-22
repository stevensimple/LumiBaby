import SwiftUI

@main
struct LumiBabyApp: App {
    @StateObject private var auth = AuthService.shared
    @StateObject private var ws = WebSocketService.shared

    var body: some Scene {
        WindowGroup {
            Group {
                if auth.isAuthenticated {
                    MainTabView()
                        .environmentObject(auth)
                        .environmentObject(ws)
                        .onAppear { ws.connect() }
                        .onDisappear { ws.disconnect() }
                } else {
                    LoginView().environmentObject(auth)
                }
            }
            .preferredColorScheme(.dark)
        }
    }
}

struct MainTabView: View {
    @EnvironmentObject var ws: WebSocketService

    var body: some View {
        TabView {
            HomeView()
                .tabItem { Label("Accueil", systemImage: "house.fill") }
            SleepView()
                .tabItem { Label("Sommeil", systemImage: "moon.zzz.fill") }
            SensorsView()
                .tabItem { Label("Capteur", systemImage: "sensor.tag.radiowaves.forward") }
            AlertsView()
                .tabItem { Label("Alertes", systemImage: "bell.fill") }
            SettingsView()
                .tabItem { Label("Réglages", systemImage: "gearshape.fill") }
        }
        .environmentObject(ws)
        .tint(LumiColor.primary)
    }
}
