function [left, right] = fft_convolve_mono_to_stereo(audio, hrir_l, hrir_r)
% FFT_CONVOLVE_MONO_TO_STEREO Convolve mono audio with HRIR left/right
% Returns full convolution (mode='full')
if ndims(audio) ~= 2 && ~isvector(audio)
    error('Audio must be mono vector');
end
audio = audio(:)';
left = conv(audio, hrir_l(:)');
right = conv(audio, hrir_r(:)');
end

function y = normalize_audio(sig)
    peak = max(abs(sig(:)));
    if peak <= 0
        y = sig;
    else
        y = sig / peak;
    end
end
