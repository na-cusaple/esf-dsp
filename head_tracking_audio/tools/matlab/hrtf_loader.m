function dataset = load_cipic_mat(mat_path, target_sample_rate, source_sample_rate)
% LOAD_CIPIC_MAT Load CIPIC .mat and optionally resample HRIR to target Fs
% dataset = load_cipic_mat(mat_path, target_sample_rate, source_sample_rate)

data = load(mat_path);

if isfield(data,'hrir_l') && isfield(data,'hrir_r') && isfield(data,'azim_v') && isfield(data,'elev_v')
    hrir_l = double(data.hrir_l);
    hrir_r = double(data.hrir_r);
    azim = double(data.azim_v(:));
    elev = double(data.elev_v(:));
else
    error('Missing CIPIC keys: hrir_l/hrir_r/azim_v/elev_v');
end

% extract sample rate if present
fs = 0;
keys = {'fs','Fs','sampling_rate','sample_rate'};
for k = 1:numel(keys)
    if isfield(data,keys{k})
        val = data.(keys{k});
        if ~isempty(val)
            fs = double(val(1));
            break
        end
    end
end
if fs == 0 && exist('source_sample_rate','var') && ~isempty(source_sample_rate)
    fs = double(source_sample_rate);
end

if exist('target_sample_rate','var') && ~isempty(target_sample_rate) && fs>0 && target_sample_rate~=fs
    % resample along last dimension (samples)
    target_sample_rate = double(target_sample_rate);
    [hrir_l,hrir_r] = resample_hrir_3d(hrir_l,hrir_r,fs,target_sample_rate);
    fs = target_sample_rate;
end

dataset.hrir_l = hrir_l;
dataset.hrir_r = hrir_r;
dataset.azimuths = azim;
dataset.elevations = elev;
dataset.sample_rate = fs;
end

function [hl_rs, hr_rs] = resample_hrir_3d(hl, hr, srcFs, dstFs)
    % hl/hr assumed dims: elev x azim x samples OR azim x elev x samples
    sz = size(hl);
    nd = numel(sz);
    if nd < 3
        error('Unexpected HRIR array dimensions');
    end
    % assume samples are along 3rd dim
    S = sz(3);
    % preallocate
    % compute up/down
    g = gcd(srcFs,dstFs);
    p = dstFs/g;
    q = srcFs/g;
    % reshape to 2D (Npairs x samples)
    nPairs = sz(1)*sz(2);
    hl2 = reshape(hl, [nPairs, S]);
    hr2 = reshape(hr, [nPairs, S]);
    hl_rs2 = zeros(nPairs, ceil(S*p/q));
    hr_rs2 = zeros(nPairs, ceil(S*p/q));
    for i=1:nPairs
        hl_rs2(i,:) = resample(hl2(i,:), p, q);
        hr_rs2(i,:) = resample(hr2(i,:), p, q);
    end
    newS = size(hl_rs2,2);
    hl_rs = reshape(hl_rs2, [sz(1), sz(2), newS]);
    hr_rs = reshape(hr_rs2, [sz(1), sz(2), newS]);
end
