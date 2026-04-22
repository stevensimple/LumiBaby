import SwiftUI

struct AlertsView: View {
    @StateObject private var vm = AlertsViewModel()

    var body: some View {
        ZStack {
            LumiColor.background.ignoresSafeArea()
            VStack(spacing: 0) {
                HStack {
                    Text("Alertes")
                        .font(LumiFont.title)
                        .foregroundStyle(LumiColor.textPrimary)
                    Spacer()
                    if !vm.alerts.isEmpty {
                        Text("\(vm.alerts.count)")
                            .font(LumiFont.captionBold)
                            .padding(.horizontal, 8).padding(.vertical, 4)
                            .background(LumiColor.alert.opacity(0.2))
                            .foregroundStyle(LumiColor.alert)
                            .clipShape(Capsule())
                    }
                }
                .padding(.horizontal, 24).padding(.top, 8).padding(.bottom, 16)

                if vm.isLoading {
                    Spacer()
                    ProgressView().tint(LumiColor.primary)
                    Spacer()
                } else if vm.alerts.isEmpty {
                    Spacer()
                    VStack(spacing: 12) {
                        Image(systemName: "moon.zzz.fill")
                            .font(.system(size: 48))
                            .foregroundStyle(LumiColor.primary)
                        Text("Tout va bien")
                            .font(LumiFont.title2)
                            .foregroundStyle(LumiColor.textPrimary)
                        Text("Aucune alerte — bébé est tranquille")
                            .font(LumiFont.body)
                            .foregroundStyle(LumiColor.textSecondary)
                    }
                    Spacer()
                } else {
                    ScrollView(showsIndicators: false) {
                        LazyVStack(spacing: 12) {
                            ForEach(vm.alerts) { alert in
                                AlertCard(alert: alert) {
                                    await vm.acknowledge(id: alert.id)
                                }
                            }
                        }
                        .padding(.horizontal, 20)
                    }
                }
            }
        }
        .task { await vm.load() }
        .refreshable { await vm.load() }
    }
}

private struct AlertCard: View {
    let alert: AlertItem
    let onDismiss: () async -> Void

    private var color: Color {
        switch alert.severity {
        case "critical": return LumiColor.alert
        case "warning":  return LumiColor.movement
        default:         return LumiColor.primary
        }
    }

    private var icon: String {
        switch alert.type {
        case "presence_lost":        return "questionmark.circle.fill"
        case "prolonged_inactivity": return "timer"
        case "unusual_activity":     return "waveform.path"
        case "wake_event":           return "moon.zzz"
        default:                     return "info.circle"
        }
    }

    private var message: String {
        switch alert.type {
        case "presence_lost":        return "Bébé non détecté dans le berceau"
        case "prolonged_inactivity": return alert.message
        case "unusual_activity":     return "Activité inhabituelle détectée"
        case "wake_event":           return "Réveil détecté"
        default:                     return alert.message
        }
    }

    var body: some View {
        HStack(spacing: 14) {
            ZStack {
                Circle().fill(color.opacity(0.15)).frame(width: 42, height: 42)
                Image(systemName: icon).foregroundStyle(color).font(.system(size: 18))
            }
            VStack(alignment: .leading, spacing: 3) {
                Text(message)
                    .font(LumiFont.body)
                    .foregroundStyle(LumiColor.textPrimary)
                Text(alert.createdAt)
                    .font(LumiFont.caption)
                    .foregroundStyle(LumiColor.textSecondary)
            }
            Spacer()
            Button { Task { await onDismiss() } } label: {
                Image(systemName: "xmark")
                    .font(.caption)
                    .foregroundStyle(LumiColor.textSecondary)
            }
        }
        .padding(16)
        .lumiCard()
    }
}
