% Spatial Audio analysis utilities (MATLAB)
% Usage:
%  - Edit paths below or call functions directly.
%  - Requires Signal Processing Toolbox (resample) for high-quality resampling.
%
% Demo examples included at the bottom show:
%  1) HRIR resampling and impulse test
%  2) HRIR selection + overlap-add block convolution
%  3) NLERP usage
%  4) Compute EMA time offset from UART CSV log

function spatial_audio_analysis_demo()
    % Demo wrapper — edit paths as needed
    % Set paths
    hrir_mat = fullfile('..','..','hrtf','hrir_final_003.mat'); % change as needed
    wav_in = fullfile('..','..','audio','test_tone.wav');
    csv_log = fullfile('..','..','logs','serial_log.csv'); % optional

    fprintf('Demo: HRIR resample and impulse test\n');
    if exist(hrir_mat,'file')
        data = load(hrir_mat);
        % CIPIC commonly stores hrir_l/h rir_r as 3D arrays
        if isfield(data,'hrir_l') && isfield(data,'hrir_r')
            hrir_l = double(data.hrir_l);
            hrir_r = double(data.hrir_r);
            az = double(data.azim_v(:));
            el = double(data.elev_v(:));
            srcFs = try_extract_fs(data);
            dstFs = 48000;
            % select one HRIR (example first elevation, first azimuth)
            hl = squeeze(hrir_l(1,1,:))';
            hr = squeeze(hrir_r(1,1,:))';
            hl_rs = resample_hrir(hl,srcFs,dstFs);
            hr_rs = resample_hrir(hr,srcFs,dstFs);
            fprintf('Original len %d -> resampled len %d (Fs %d -> %d)\n', numel(hl), numel(hl_rs), srcFs, dstFs);
            impulse_test(hl,hl_rs,dstFs);
        else
            warning('HRIR keys not found in MAT file');
        end
    else
        warning('HRIR .mat not found: %s', hrir_mat);
    end

    fprintf('\nDemo: NLERP example\n');
    q0 = [1 0 0 0];
    q1 = [0.7071 0 0.7071 0];
    for a = [0 0.25 0.5 0.75 1]
        q = nlerp(q0,q1,a);
        fprintf('alpha=%.2f -> q=[%.4f %.4f %.4f %.4f]\n', a, q);
    end

    fprintf('\nIf you have a CSV serial log, compute EMA offset:\n');
    if exist(csv_log,'file')
        [tau,uart_delay] = compute_ema_offset(csv_log,0.01);
        fprintf('Last tau=%.4f s, last uart_delay=%.4f s\n', tau(end), uart_delay(end));
        figure; plot(1000*(uart_delay)); xlabel('sample'); ylabel('uart delay (ms)'); title('UART delay over time');
    else
        fprintf('CSV log not found: %s (skipping)\n', csv_log);
    end
end

function fs = try_extract_fs(data)
    keys = {'fs','Fs','sampling_rate','sample_rate'};
    fs = 0;
    for k = 1:numel(keys)
        if isfield(data,keys{k})
            val = data.(keys{k});
            if ~isempty(val)
                fs = double(val(1));
                return
            end
        end
    end
    if fs==0
        fs = 44100; % fallback
    end
end

function y = resample_hrir(h, srcFs, dstFs)
    if isempty(srcFs) || srcFs==0
        srcFs = 44100;
    end
    if srcFs == dstFs
        y = h;
        return
    end
    % compute integer up/down factors via gcd
    g = gcd(srcFs,dstFs);
    p = dstFs/g;
    q = srcFs/g;
    % use MATLAB resample (FIR anti-aliasing)
    y = resample(h, p, q); % requires Signal Processing Toolbox
end

function impulse_test(h_orig,h_resampled,Fs)
    % compare impulse responses in time and frequency
    L1 = numel(h_orig);
    L2 = numel(h_resampled);
    t1 = (0:L1-1)/Fs;
    t2 = (0:L2-1)/Fs;
    figure;
    subplot(2,1,1); plot(t1,h_orig); title('Original HRIR (time)'); xlabel('s');
    subplot(2,1,2); plot(t2,h_resampled); title('Resampled HRIR (time)'); xlabel('s');
    % frequency magnitude
    N = 2^nextpow2(max(L1,L2));
    H1 = fft(h_orig,N);
    H2 = fft(h_resampled,N);
    f = (0:N-1)/N*Fs;
    figure; plot(f,20*log10(abs(H1)+eps)); hold on; plot(f,20*log10(abs(H2)+eps)); xlim([0 Fs/2]); legend('orig','resampled'); title('Magnitude response');
end

function q = nlerp(q0,q1,alpha)
    % input as 1x4 vectors [w x y z]
    q0 = q0./norm(q0);
    q1 = q1./norm(q1);
    d = dot(q0,q1);
    if d < 0
        q1 = -q1;
    end
    qtemp = (1-alpha)*q0 + alpha*q1;
    q = qtemp./norm(qtemp);
end

function [tau_seq, uart_delay] = compute_ema_offset(csvfile, gamma)
    % csv lines: qw,qx,qy,qz,timestamp_ms\n
    fid = fopen(csvfile,'r');
    if fid < 0
        error('Cannot open %s', csvfile);
    end
    tau = [];
    uart_delay = [];
    tau_curr = NaN;
    idx = 0;
    while ~feof(fid)
        line = fgetl(fid);
        if isempty(line) || ~ischar(line)
            continue
        end
        parts = strsplit(line,',');
        if numel(parts) < 5
            continue
        end
        t_ms = str2double(parts{5});
        if isnan(t_ms)
            continue
        end
        t_dev = t_ms/1000;
        t_host = now_to_perf();
        if isnan(tau_curr)
            tau_curr = t_host - t_dev;
        else
            tau_curr = (1-gamma)*tau_curr + gamma*(t_host - t_dev);
        end
        idx = idx + 1;
        tau(idx) = tau_curr; %#ok<AGROW>
        uart_delay(idx) = t_host - (t_dev + tau_curr); %#ok<AGROW>
    end
    fclose(fid);
    tau_seq = tau;
end

function t = now_to_perf()
    % high resolution clock approximate using tic/toc relative to persistent base
    persistent t0
    if isempty(t0)
        t0 = tic;
    end
    t = toc(t0);
end
