import SwiftUI

struct SensorsView: View {
    @StateObject private var vm = SensorsViewModel()
    @State private var showAdd = false

    var body: some View {
        ZStack {
            LumiColor.background.ignoresSafeArea()
            ScrollView(showsIndicators: false) {
                VStack(spacing: 16) {
                    HStack {
                        Text("Capteurs")
                            .font(LumiFont.title)
                            .foregroundStyle(LumiColor.textPrimary)
                        Spacer()
                        Button { showAdd = true } label: {
                            Image(systemName: "plus.circle.fill")
                                .font(.title2)
                                .foregroundStyle(LumiColor.primary)
                        }
                    }
                    .padding(.horizontal, 24)
                    .padding(.top, 8)

                    if vm.isLoading {
                        ProgressView().tint(LumiColor.primary).padding(.top, 60)
                    } else if vm.sensors.isEmpty {
                        VStack(spacing: 16) {
                            Image(systemName: "sensor.tag.radiowaves.forward")
                                .font(.system(size: 48))
                                .foregroundStyle(LumiColor.textSecondary)
                            Text("Aucun capteur configuré")
                                .font(LumiFont.headline)
                                .foregroundStyle(LumiColor.textSecondary)
                            Text("Ajoutez votre capteur ESP32 pour commencer")
                                .font(LumiFont.body)
                                .foregroundStyle(LumiColor.textSecondary)
                                .multilineTextAlignment(.center)
                        }
                        .padding(.top, 60)
                    } else {
                        ForEach(vm.sensors) { sensor in
                            SensorDetailCard(sensor: sensor)
                                .padding(.horizontal, 20)
                        }
                    }
                }
                .padding(.bottom, 32)
            }
        }
        .task { await vm.load() }
        .refreshable { await vm.load() }
        .sheet(isPresented: $showAdd) {
            AddSensorSheet(isPresented: $showAdd) { await vm.load() }
        }
    }
}

private struct SensorDetailCard: View {
    let sensor: Sensor
    @State private var health: SensorHealth?

    var body: some View {
        VStack(spacing: 16) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(sensor.name)
                        .font(LumiFont.headline)
                        .foregroundStyle(LumiColor.textPrimary)
                    if let loc = sensor.location {
                        Text(loc)
                            .font(LumiFont.caption)
                            .foregroundStyle(LumiColor.textSecondary)
                    }
                }
                Spacer()
                StatusPill(online: sensor.isOnline)
            }

            Divider().background(LumiColor.separator)

            HStack(spacing: 0) {
                SensorMetric(
                    value: health.map { "\(Int($0.signalQuality * 100))%" } ?? "—",
                    label: "Signal",
                    icon: "wifi"
                )
                SensorMetric(
                    value: health.map { String(format: "%.1f", $0.packetRate) } ?? "—",
                    label: "Paquets/s",
                    icon: "arrow.down"
                )
                SensorMetric(
                    value: sensor.isOnline ? "Actif" : "Hors ligne",
                    label: "État",
                    icon: "circle.fill"
                )
            }

            if sensor.isOnline {
                Button {
                    // placeholder for placement optimization
                } label: {
                    Label("Optimiser le placement", systemImage: "arrow.triangle.2.circlepath")
                        .font(LumiFont.captionBold)
                        .foregroundStyle(LumiColor.primary)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 10)
                        .background(LumiColor.primary.opacity(0.1))
                        .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
                }
            }
        }
        .padding(20)
        .lumiCard()
        .task {
            health = try? await APIService.shared.fetchSensorHealth(sensorId: sensor.sensorId)
        }
    }
}

private struct StatusPill: View {
    let online: Bool
    var body: some View {
        HStack(spacing: 4) {
            Circle()
                .fill(online ? LumiColor.calm : LumiColor.alert)
                .frame(width: 6, height: 6)
            Text(online ? "Connecté" : "Hors ligne")
                .font(LumiFont.captionBold)
                .foregroundStyle(online ? LumiColor.calm : LumiColor.alert)
        }
        .padding(.horizontal, 10).padding(.vertical, 5)
        .background((online ? LumiColor.calm : LumiColor.alert).opacity(0.12))
        .clipShape(Capsule())
    }
}

private struct SensorMetric: View {
    let value: String
    let label: String
    let icon: String

    var body: some View {
        VStack(spacing: 4) {
            Image(systemName: icon).font(.caption).foregroundStyle(LumiColor.primary)
            Text(value).font(LumiFont.captionBold).foregroundStyle(LumiColor.textPrimary)
            Text(label).font(LumiFont.caption).foregroundStyle(LumiColor.textSecondary)
        }
        .frame(maxWidth: .infinity)
    }
}

private struct AddSensorSheet: View {
    @Binding var isPresented: Bool
    @State private var sensorId = ""
    @State private var name = ""
    @State private var isLoading = false
    let onAdd: () async -> Void

    var body: some View {
        NavigationStack {
            Form {
                Section("Identifiant du capteur") {
                    TextField("ex: esp32_001", text: $sensorId).autocorrectionDisabled()
                }
                Section("Nom") {
                    TextField("ex: Chambre de Léo", text: $name)
                }
            }
            .navigationTitle("Ajouter un capteur")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Annuler") { isPresented = false }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Ajouter") { Task { await add() } }
                        .disabled(sensorId.isEmpty || name.isEmpty || isLoading)
                }
            }
        }
    }

    private func add() async {
        isLoading = true
        var req = URLRequest(url: APIService.shared.url("/api/v1/sensors"))
        req.httpMethod = "POST"
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        if let t = AuthService.shared.token {
            req.setValue("Bearer \(t)", forHTTPHeaderField: "Authorization")
        }
        req.httpBody = try? JSONEncoder().encode(["sensor_id": sensorId, "name": name])
        _ = try? await URLSession.shared.data(for: req)
        await onAdd()
        isPresented = false
    }
}
