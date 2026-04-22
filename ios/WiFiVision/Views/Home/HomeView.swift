import SwiftUI

struct HomeView: View {
    @StateObject private var vm = HomeViewModel()
    @EnvironmentObject private var ws: WebSocketService
    @AppStorage("roomName") private var roomName = "Chambre de bébé"

    var body: some View {
        ZStack {
            LumiColor.background.ignoresSafeArea()

            ScrollView(showsIndicators: false) {
                VStack(spacing: 20) {
                    // Header
                    HStack {
                        VStack(alignment: .leading, spacing: 2) {
                            Text("LumiBaby")
                                .font(LumiFont.title)
                                .foregroundStyle(LumiColor.textPrimary)
                            Text(roomName)
                                .font(LumiFont.caption)
                                .foregroundStyle(LumiColor.textSecondary)
                        }
                        Spacer()
                        HStack(spacing: 6) {
                            Circle()
                                .fill(ws.isConnected ? LumiColor.calm : LumiColor.movement)
                                .frame(width: 8, height: 8)
                            Text(ws.isConnected ? "En direct" : "Reconnexion…")
                                .font(LumiFont.caption)
                                .foregroundStyle(LumiColor.textSecondary)
                        }
                    }
                    .padding(.horizontal, 24)
                    .padding(.top, 8)

                    // Main status card
                    MainStatusCard(vm: vm)
                        .padding(.horizontal, 20)

                    // Inactivity warning
                    if let warning = vm.inactivityWarning {
                        HStack(spacing: 10) {
                            Image(systemName: "bell.badge.fill")
                                .foregroundStyle(LumiColor.movement)
                                .font(.subheadline)
                            Text(warning)
                                .font(LumiFont.body)
                                .foregroundStyle(LumiColor.textPrimary)
                            Spacer()
                        }
                        .padding(.horizontal, 16)
                        .padding(.vertical, 12)
                        .background(LumiColor.movement.opacity(0.12))
                        .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
                        .padding(.horizontal, 20)
                    }

                    // Quick info row
                    HStack(spacing: 12) {
                        QuickInfoCard(icon: "moon.zzz", label: "Sommeil", value: vm.sleepDurationText)
                        QuickInfoCard(icon: "figure.roll", label: "Dernier mvt", value: vm.lastMovementText)
                        QuickInfoCard(icon: "wifi", label: "Signal", value: "Bon")
                    }
                    .padding(.horizontal, 20)

                    Spacer(minLength: 32)
                }
            }
        }
        .navigationBarHidden(true)
    }
}

// MARK: - Main Status Card

private struct MainStatusCard: View {
    @ObservedObject var vm: HomeViewModel
    @State private var pulse = false

    var body: some View {
        ZStack(alignment: .bottom) {
            // Background gradient
            RoundedRectangle(cornerRadius: 28, style: .continuous)
                .fill(
                    LinearGradient(
                        colors: [vm.mainStateColor.opacity(0.22), LumiColor.card],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )

            // Wave animation
            AnimatedWaves(color: vm.mainStateColor)
                .frame(height: 80)
                .clipShape(RoundedRectangle(cornerRadius: 28, style: .continuous))
                .frame(maxHeight: .infinity, alignment: .bottom)
                .opacity(vm.babyDetected ? 1 : 0.3)

            // Content
            VStack(spacing: 22) {
                // Pulse icon
                ZStack {
                    Circle()
                        .fill(vm.mainStateColor.opacity(0.15))
                        .frame(width: 88, height: 88)
                        .scaleEffect(pulse ? 1.12 : 1.0)
                        .animation(.easeInOut(duration: 2.5).repeatForever(autoreverses: true), value: pulse)
                    Image(systemName: vm.mainStateIcon)
                        .font(.system(size: 38, weight: .medium))
                        .foregroundStyle(vm.mainStateColor)
                }
                .onAppear { pulse = vm.babyDetected }
                .onChange(of: vm.babyDetected) { newVal in pulse = newVal }

                // State label
                Text(vm.mainStateText)
                    .font(LumiFont.title)
                    .foregroundStyle(LumiColor.textPrimary)
                    .multilineTextAlignment(.center)

                // Score
                ScoreChip(score: vm.activityScore, label: vm.scoreLabel, color: vm.mainStateColor)
            }
            .padding(.horizontal, 28)
            .padding(.vertical, 36)
        }
        .frame(minHeight: 300)
    }
}

// MARK: - Score Chip

private struct ScoreChip: View {
    let score: Int
    let label: String
    let color: Color

    var body: some View {
        HStack(spacing: 10) {
            ZStack {
                Circle()
                    .trim(from: 0, to: CGFloat(score) / 100)
                    .stroke(color, style: StrokeStyle(lineWidth: 3, lineCap: .round))
                    .rotationEffect(.degrees(-90))
                    .frame(width: 32, height: 32)
                Circle()
                    .stroke(color.opacity(0.2), lineWidth: 3)
                    .frame(width: 32, height: 32)
                Text("\(score)")
                    .font(.system(size: 10, weight: .bold, design: .rounded))
                    .foregroundStyle(color)
            }
            Text(label)
                .font(LumiFont.captionBold)
                .foregroundStyle(LumiColor.textPrimary)
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 8)
        .background(LumiColor.card.opacity(0.8))
        .clipShape(Capsule())
    }
}

// MARK: - Quick Info Card

private struct QuickInfoCard: View {
    let icon: String
    let label: String
    let value: String

    var body: some View {
        VStack(spacing: 6) {
            Image(systemName: icon)
                .font(.system(size: 16))
                .foregroundStyle(LumiColor.primary)
            Text(value)
                .font(LumiFont.captionBold)
                .foregroundStyle(LumiColor.textPrimary)
                .lineLimit(1)
                .minimumScaleFactor(0.7)
            Text(label)
                .font(LumiFont.caption)
                .foregroundStyle(LumiColor.textSecondary)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 14)
        .lumiCard()
    }
}
