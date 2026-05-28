% run_spatial_sim.m
% Offline MATLAB runner for spatial audio pipeline (mono->binaural)
% Requirements: MATLAB + Signal Processing Toolbox (resample). Edit paths below.

%% User parameters (edit as needed)
hrir_mat = fullfile('..','..','hrtf','hrir_final_003.mat');
wav_in = fullfile('..','..','audio','test_tone.wav');
csv_log = fullfile('..','..','logs','serial_log.csv'); % optional
out_wav = fullfile('..','..','audio','out_spatial.wav');
targetFs = 48000;      % desired audio sample rate
block_size = 256;      % block size for OLA
yaw_deg = 30; pitch_deg = 0; % example listening direction

%% Prepare environment
addpath(fileparts(mfilename('fullpath')));

if ~exist(hrir_mat,'file')
    error('HRIR .mat not found: %s', hrir_mat);
end
if ~exist(wav_in,'file')
    error('Input WAV not found: %s', wav_in);
end

%% Load and resample HRTF
fprintf('Loading HRTF...\n');
dataset = load_cipic_mat(hrir_mat, targetFs);
fprintf('Dataset sample rate: %d Hz\n', dataset.sample_rate);

%% Select interpolated HRIR for yaw/pitch
[hl, hr, used0, used1, alpha] = select_hrir_interpolated(dataset, yaw_deg, pitch_deg);
fprintf('Selected HRIR (interpolated): az %g / %g (alpha=%.3f)\n', used0, used1, alpha);

%% Create overlap-add convolver
conv = OverlapAddConvolver(hl, hr, block_size);

%% Read input audio and ensure mono
[x, fs] = audioread(wav_in);
if size(x,2) > 1
    x = mean(x,2);
end
if fs ~= targetFs
    fprintf('Resampling input audio %d -> %d\n', fs, targetFs);
    g = gcd(fs,targetFs);
    p = targetFs/g; q = fs/g;
    x = resample(x, p, q);
    fs = targetFs;
end

%% Process in blocks (simulate realtime callback)
n = numel(x);
nBlocks = ceil(n / block_size);
outL = zeros(nBlocks*block_size,1);
outR = zeros(nBlocks*block_size,1);
idx = 1;
for b = 1:nBlocks
    start = (b-1)*block_size + 1;
    stop = min(b*block_size, n);
    blk = zeros(block_size,1);
    blk(1:(stop-start+1)) = x(start:stop);
    [ol, or] = conv.process(blk'); % conv expects row vector
    outL(idx:idx+block_size-1) = ol(:);
    outR(idx:idx+block_size-1) = or(:);
    idx = idx + block_size;
end

stereo = [outL(1:n) outR(1:n)];
stereo = stereo / max(abs(stereo(:))+eps);

fprintf('Writing output: %s\n', out_wav);
audiowrite(out_wav, stereo, fs);

%% Optional: compute EMA offset from CSV log
if exist(csv_log,'file')
    fprintf('Computing EMA offset from CSV...\n');
    [tau_seq, uart_delay] = compute_ema_offset(csv_log, 0.01);
    figure; plot(1000*uart_delay); xlabel('sample'); ylabel('UART delay (ms)'); title('UART delay');
end

fprintf('Done. Play output with: sound([stereo(:,1) stereo(:,2)], %d)\n', fs);
