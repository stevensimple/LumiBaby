import SwiftUI

struct SleepView: View {
    @StateObject private var vm = SleepViewModel()
    @State private var sensors: [Sensor] = []
    @State private var selectedSensorId: String = ""

    var body: some View {
        ZStack {
            LumiColor.background.ignoresSafeArea()
            ScrollView(showsIndicators: false) {
                VStack(spacing: 20) {
                    // Header
                    HStack {
                        Text("Sommeil")
                            .font(LumiFont.title)
                            .foregroundStyle(LumiColor.textPrimary)
                        Spacer()
                    }
                    .padding(.horizontal, 24)
                    .padding(.top, 8)

                    if vm.isLoading {
                        ProgressView().tint(LumiColor.primary).padding(.top, 60)
                    } else {
                        // Tonight card
                        TonightCard(vm: vm)
                            .padding(.horizontal, 20)

                        // Timeline
                        if let session = vm.tonightSession,
                           let pts = session.timeline,
                           !pts.isEmpty {
                            VStack(alignment: .leading, spacing: 12) {
                                SleepTimelineView(points: pts, startTime: nil)
                            }
                            .padding(20)
                            .lumiCard()
                            .padding(.horizontal, 20)
                        }

                        // Weekly trend
                        if let weekly = vm.weekly, !weekly.days.isEmpty {
                            WeeklyCard(weekly: weekly)
                                .padding(.horizontal, 20)
                        }

                        // Insight
                        InsightCard(text: vm.insightText)
                            .padding(.horizontal, 20)
                    }

                    Spacer(minLength: 32)
                }
            }
        }
        .task {
            sensors = (try? await APIService.shared.fetchSensors()) ?? []
            if let first = sensors.first {
                selectedSensorId = first.sensorId
                await vm.load(sensorId: first.sensorId)
            }
        }
        .refreshable {
            await vm.load(sensorId: selectedSensorId)
        }
    }
}

// MARK: - Tonight Card

private struct TonightCard: View {
    @ObservedObject var vm: SleepViewModel

    var body: some View {
        VStack(spacing: 20) {
            HStack {
                Text("Cette nuit")
                    .font(LumiFont.headline)
                    .foregroundStyle(LumiColor.textPrimary)
                Spacer()
                if let label = vm.tonightSession?.qualityLabel {
                    Text(label)
                        .font(LumiFont.captionBold)
                        .padding(.horizontal, 10).padding(.vertical, 4)
                        .background(vm.qualityColor.opacity(0.2))
                        .foregroundStyle(vm.qualityColor)
                        .clipShape(Capsule())
                }
            }

            HStack(spacing: 0) {
                SleepStat(value: vm.startTimeText, label: "Endormi à", icon: "moon.fill")
                Divider().background(LumiColor.separator).frame(height: 40)
                SleepStat(value: vm.durationText, label: "Durée", icon: "clock")
                Divider().background(LumiColor.separator).frame(height: 40)
                SleepStat(
                    value: "\(vm.tonightSession?.wakeEventsCount ?? 0)",
                    label: "Réveils",
                    icon: "waveform.path"
                )
            }

            // Score gauge
            if let score = vm.tonightSession?.sleepScore {
                HStack(spacing: 12) {
                    Text("Score de nuit")
                        .font(LumiFont.caption)
                        .foregroundStyle(LumiColor.textSecondary)
                    Spacer()
                    Text("\(score)/100")
                        .font(LumiFont.captionBold)
                        .foregroundStyle(vm.qualityColor)
                }
                GeometryReader { geo in
                    ZStack(alignment: .leading) {
                        RoundedRectangle(cornerRadius: 4)
                            .fill(LumiColor.cardLight)
                            .frame(height: 8)
                        RoundedRectangle(cornerRadius: 4)
                            .fill(vm.qualityColor)
                            .frame(width: geo.size.width * CGFloat(score) / 100, height: 8)
                    }
                }
                .frame(height: 8)
            }
        }
        .padding(20)
        .lumiCard()
    }
}

private struct SleepStat: View {
    let value: String
    let label: String
    let icon: String

    var body: some View {
        VStack(spacing: 4) {
            Image(systemName: icon).font(.caption).foregroundStyle(LumiColor.primary)
            Text(value).font(LumiFont.title2).foregroundStyle(LumiColor.textPrimary).lineLimit(1)
            Text(label).font(LumiFont.caption).foregroundStyle(LumiColor.textSecondary)
        }
        .frame(maxWidth: .infinity)
    }
}

// MARK: - Weekly Card

private struct WeeklyCard: View {
    let weekly: WeeklyTrend

    var body: some View {
        VStack(spacing: 16) {
            HStack {
                Text("Cette semaine")
                    .font(LumiFont.headline)
                    .foregroundStyle(LumiColor.textPrimary)
                Spacer()
                Text("Score moy. \(weekly.avgScore)/100")
                    .font(LumiFont.caption)
                    .foregroundStyle(LumiColor.textSecondary)
            }

            HStack(alignment: .bottom, spacing: 8) {
                ForEach(weekly.days.reversed()) { day in
                    WeekBarView(day: day)
                }
            }
            .frame(height: 80)

            HStack {
                Label("Durée moy: \(String(format: "%.1f", weekly.avgDurationHours))h", systemImage: "clock")
                Spacer()
                Label("Régularité: \(weekly.consistencyScore)%", systemImage: "checkmark.circle")
            }
            .font(LumiFont.caption)
            .foregroundStyle(LumiColor.textSecondary)
        }
        .padding(20)
        .lumiCard()
    }
}

private struct WeekBarView: View {
    let day: DaySummary

    private var barColor: Color {
        if day.sleepScore >= 75 { return LumiColor.calm }
        if day.sleepScore >= 50 { return LumiColor.movement }
        return LumiColor.alert
    }

    private var shortDate: String {
        let f = DateFormatter(); f.dateFormat = "yyyy-MM-dd"
        guard let d = f.date(from: day.date) else { return "" }
        let df = DateFormatter(); df.dateFormat = "EEE"
        df.locale = Locale(identifier: "fr_FR")
        return df.string(from: d)
    }

    var body: some View {
        VStack(spacing: 4) {
            RoundedRectangle(cornerRadius: 4)
                .fill(barColor)
                .frame(height: CGFloat(day.sleepScore) * 0.6 + 10)
            Text(shortDate)
                .font(LumiFont.caption)
                .foregroundStyle(LumiColor.textSecondary)
        }
        .frame(maxWidth: .infinity)
    }
}

// MARK: - Insight Card

private struct InsightCard: View {
    let text: String
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: "lightbulb.fill").foregroundStyle(.yellow).font(.title3)
            Text(text).font(LumiFont.body).foregroundStyle(LumiColor.textPrimary)
            Spacer()
        }
        .padding(16)
        .lumiCard()
    }
}
