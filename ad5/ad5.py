import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons
from scipy import signal

# глобальні змінні для шуму
current_noise = None
last_noise_mean = None
last_noise_cov = None
last_t_length = 0

def harmonic_with_noise(t, amplitude, frequency, phase, noise_mean, noise_covariance, show_noise=True):
    global current_noise, last_noise_mean, last_noise_cov, last_t_length

    clean_signal = amplitude * np.sin(2 * np.pi * frequency * t + phase)

    if (noise_mean != last_noise_mean or
        noise_covariance != last_noise_cov or
        len(t) != last_t_length or
        current_noise is None):

        current_noise = np.random.normal(noise_mean, np.sqrt(noise_covariance), len(t))
        last_noise_mean = noise_mean
        last_noise_cov = noise_covariance
        last_t_length = len(t)

    noise = current_noise if len(current_noise) == len(t) else np.random.normal(noise_mean, np.sqrt(noise_covariance), len(t))
    return clean_signal + (noise if show_noise else 0), clean_signal

def update(val):
    amp = s_amp.val
    freq = s_freq.val
    phase = s_phase.val
    noise_mean = s_noise_mean.val
    noise_cov = s_noise_cov.val
    cutoff = s_cutoff.val

    noisy, clean = harmonic_with_noise(t, amp, freq, phase, noise_mean, noise_cov, show_noise_btn.get_status()[0])

    full_noisy, _ = harmonic_with_noise(t, amp, freq, phase, noise_mean, noise_cov, show_noise=True)
    b, a = signal.butter(4, cutoff, fs=100)
    filtered = signal.filtfilt(b, a, full_noisy)

    line_signal.set_ydata(noisy)
    line_filtered.set_ydata(filtered)
    ax.set_ylim(min(min(noisy), min(filtered)) - 0.2, max(max(noisy), max(filtered)) + 0.2)
    fig.canvas.draw_idle()

def reset(event):
    s_amp.reset()
    s_freq.reset()
    s_phase.reset()
    s_noise_mean.reset()
    s_noise_cov.reset()
    s_cutoff.reset()
    show_noise_btn.set_active(0)

# параметри
t = np.linspace(0, 10, 1000)
init_amp = 1.0
init_freq = 0.5
init_phase = 0.0
init_mean = 0.0
init_cov = 0.1
init_cutoff = 2.0

# фігура
fig, ax = plt.subplots(figsize=(10, 7))
plt.subplots_adjust(left=0.1, bottom=0.4)

# сигнали
noisy, clean = harmonic_with_noise(t, init_amp, init_freq, init_phase, init_mean, init_cov, show_noise=True)
b, a = signal.butter(4, init_cutoff, fs=100)
filtered = signal.filtfilt(b, a, noisy)

line_signal, = plt.plot(t, noisy, label='Сигнал (з шумом)', color='orange')
line_filtered, = plt.plot(t, filtered, label='Фільтрований', color='blue')
ax.set_xlabel("Час [с]")
ax.set_ylabel("Амплітуда")
ax.legend()
ax.grid(True)

# повзунки
axcolor = 'lightgoldenrodyellow'
slider_params = {
    'facecolor': axcolor
}
ax_amp = plt.axes([0.1, 0.35, 0.65, 0.03], **slider_params)
ax_freq = plt.axes([0.1, 0.3, 0.65, 0.03], **slider_params)
ax_phase = plt.axes([0.1, 0.25, 0.65, 0.03], **slider_params)
ax_noise_mean = plt.axes([0.1, 0.2, 0.65, 0.03], **slider_params)
ax_noise_cov = plt.axes([0.1, 0.15, 0.65, 0.03], **slider_params)
ax_cutoff = plt.axes([0.1, 0.1, 0.65, 0.03], **slider_params)

s_amp = Slider(ax_amp, 'Амплітуда', 0.1, 2.0, valinit=init_amp)
s_freq = Slider(ax_freq, 'Частота', 0.1, 2.0, valinit=init_freq)
s_phase = Slider(ax_phase, 'Фаза', -np.pi, np.pi, valinit=init_phase)
s_noise_mean = Slider(ax_noise_mean, 'Шум (сер.)', -0.5, 0.5, valinit=init_mean)
s_noise_cov = Slider(ax_noise_cov, 'Шум (дисп.)', 0.001, 0.5, valinit=init_cov)
s_cutoff = Slider(ax_cutoff, 'Фільтр зрізу', 0.1, 10.0, valinit=init_cutoff)

# Reset
ax_reset = plt.axes([0.8, 0.025, 0.1, 0.04])
btn_reset = Button(ax_reset, 'Скинути', color=axcolor)

# чекбокс
ax_check = plt.axes([0.8, 0.08, 0.15, 0.04])
show_noise_btn = CheckButtons(ax_check, ['Показати шум'], [True])

# прив'язка
for slider in [s_amp, s_freq, s_phase, s_noise_mean, s_noise_cov, s_cutoff]:
    slider.on_changed(update)

show_noise_btn.on_clicked(update)
btn_reset.on_clicked(reset)

plt.show()