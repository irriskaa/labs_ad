import numpy as np
from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource, Slider, Button, CheckboxGroup
from bokeh.layouts import column, row

# глобальні змінні для шуму
current_noise = None
last_noise_mean = None
last_noise_cov = None
last_t_length = 0

# початкові параметри
t = np.linspace(0, 10, 1000)
init_params = {
    'amplitude': 1.0,
    'frequency': 0.5,
    'phase': 0.0,
    'noise_mean': 0.0,
    'noise_cov': 0.1,
    'window': 10,
}

# гармоніка + шум
def harmonic_with_noise(t, amplitude, frequency, phase, noise_mean, noise_covariance, show_noise=True):
    global current_noise, last_noise_mean, last_noise_cov, last_t_length
    clean = amplitude * np.sin(2 * np.pi * frequency * t + phase)

    if (noise_mean != last_noise_mean or noise_covariance != last_noise_cov or
        len(t) != last_t_length or current_noise is None):
        current_noise = np.random.normal(noise_mean, np.sqrt(noise_covariance), len(t))
        last_noise_mean = noise_mean
        last_noise_cov = noise_covariance
        last_t_length = len(t)

    noise = current_noise if len(current_noise) == len(t) else np.random.normal(noise_mean, np.sqrt(noise_covariance), len(t))
    return clean, clean + (noise if show_noise else 0)

# кастомний ковзний фільтр
def custom_moving_average_filter(signal, window_size=10):
    if window_size < 1:
        return signal
    kernel = np.ones(int(window_size)) / window_size
    return np.convolve(signal, kernel, mode='same')

# апдейт графіка
def update(attr, old, new):
    amp = amp_slider.value
    freq = freq_slider.value
    phase = phase_slider.value
    mean = noise_mean_slider.value
    cov = noise_cov_slider.value
    window = window_slider.value
    show_noise = 0 in checkbox.active

    clean, noisy = harmonic_with_noise(t, amp, freq, phase, mean, cov, show_noise=show_noise)
    filtered = custom_moving_average_filter(noisy, window)

    source.data = {
        'x': t,
        'clean': clean,
        'noisy': noisy,
        'filtered': filtered
    }

# reset
def reset():
    amp_slider.value = init_params['amplitude']
    freq_slider.value = init_params['frequency']
    phase_slider.value = init_params['phase']
    noise_mean_slider.value = init_params['noise_mean']
    noise_cov_slider.value = init_params['noise_cov']
    window_slider.value = init_params['window']
    checkbox.active = [0]

# source
source = ColumnDataSource(data=dict(x=t, clean=[], noisy=[], filtered=[]))

# графік 1: чистий + шум
plot1 = figure(height=300, width=800, title="Чистий та зашумлений сигнал")
plot1.line('x', 'clean', source=source, color="green", legend_label="Чистий сигнал")
plot1.line('x', 'noisy', source=source, color="orange", legend_label="З шумом")
plot1.legend.location = "top_left"

# графік 2: фільтрований
plot2 = figure(height=300, width=800, title="Фільтрований сигнал (ковзне середнє)", x_range=plot1.x_range)
plot2.line('x', 'filtered', source=source, color="blue", legend_label="Фільтрований")
plot2.legend.location = "top_left"

# слайдери
amp_slider = Slider(start=0.1, end=2.0, step=0.1, value=init_params['amplitude'], title="Амплітуда")
freq_slider = Slider(start=0.1, end=2.0, step=0.1, value=init_params['frequency'], title="Частота")
phase_slider = Slider(start=-np.pi, end=np.pi, step=0.1, value=init_params['phase'], title="Фаза")
noise_mean_slider = Slider(start=-0.5, end=0.5, step=0.01, value=init_params['noise_mean'], title="Шум (сер.)")
noise_cov_slider = Slider(start=0.001, end=0.5, step=0.01, value=init_params['noise_cov'], title="Шум (дисп.)")
window_slider = Slider(start=1, end=100, step=1, value=init_params['window'], title="Вікно фільтра")

# чекбокс
checkbox = CheckboxGroup(labels=["Показати шум"], active=[0])

# кнопка для скидання
reset_button = Button(label="Скинути", button_type="success")
reset_button.on_click(reset)

# 
for widget in [amp_slider, freq_slider, phase_slider, noise_mean_slider, noise_cov_slider, window_slider, checkbox]:
    widget.on_change('value' if isinstance(widget, Slider) else 'active', update)

# початкова ініціалізація
clean, noisy = harmonic_with_noise(
    t,
    init_params['amplitude'],
    init_params['frequency'],
    init_params['phase'],
    init_params['noise_mean'],
    init_params['noise_cov'],
    show_noise=True
)
filtered = custom_moving_average_filter(noisy, init_params['window'])
source.data = {'x': t, 'clean': clean, 'noisy': noisy, 'filtered': filtered}

# "макет"
controls = column(amp_slider, freq_slider, phase_slider,
                  noise_mean_slider, noise_cov_slider, window_slider,
                  checkbox, reset_button)
layout = row(column(plot1, plot2), controls)

curdoc().add_root(layout)
curdoc().title = "Гармоніка з шумом та власною фільтрацією"
