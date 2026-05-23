use std::sync::Mutex;
use tauri::Manager;
use tauri_plugin_shell::ShellExt;

struct SidecarState {
    child: Mutex<Option<tauri_plugin_shell::process::CommandChild>>,
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(
            tauri_plugin_log::Builder::default()
                .level(log::LevelFilter::Info)
                .build(),
        )
        .setup(|app| {
            let shell = app.shell();
            let backend_dir = std::env::current_dir()
                .unwrap_or_default()
                .parent()
                .map(|p| p.join("backend"))
                .unwrap_or_else(|| std::path::PathBuf::from("../backend"));

            let child = shell
                .command("python")
                .args(["-m", "src.main"])
                .current_dir(&backend_dir)
                .spawn()
                .expect("Failed to start Python backend sidecar");

            log::info!("Python sidecar started with PID: {:?}", child.pid());
            app.manage(SidecarState {
                child: Mutex::new(Some(child)),
            });

            Ok(())
        })
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::CloseRequested { .. } = event {
                if let Some(state) = window.app_handle().try_state::<SidecarState>() {
                    if let Ok(mut guard) = state.child.lock() {
                        if let Some(child) = guard.take() {
                            log::info!("Shutting down Python sidecar");
                            let _ = child.kill();
                        }
                    }
                }
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
