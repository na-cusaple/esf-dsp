function [left,right,used] = select_hrir(dataset, yaw_deg, pitch_deg)
% SELECT_HRIR nearest selection (no interpolation)
az = double(dataset.azimuths(:));
el = double(dataset.elevations(:));
[~, az_idx] = min(abs(az - yaw_deg));
[~, el_idx] = min(abs(el - pitch_deg));
hrir_l = dataset.hrir_l;
hrir_r = dataset.hrir_r;
% assume hrir dims elev x az x samples OR az x elev x samples -> detect
if size(hrir_l,1) == numel(el) && size(hrir_l,2) == numel(az)
    left = squeeze(hrir_l(el_idx, az_idx, :))';
    right = squeeze(hrir_r(el_idx, az_idx, :))';
elseif size(hrir_l,1) == numel(az) && size(hrir_l,2) == numel(el)
    left = squeeze(hrir_l(az_idx, el_idx, :))';
    right = squeeze(hrir_r(az_idx, el_idx, :))';
else
    error('HRIR shape does not match azimuth/elevation vectors');
end
used = [az(az_idx), el(el_idx)];
end

function [left,right,used0,used1,alpha] = select_hrir_interpolated(dataset, yaw_deg, pitch_deg)
az = double(dataset.azimuths(:));
el = double(dataset.elevations(:));
[~, el_idx] = min(abs(el - pitch_deg));
% sort azimuths
[az_sorted, order] = sort(az);
if yaw_deg <= az_sorted(1)
    idx0 = order(1); idx1 = order(1); alpha = 0;
elseif yaw_deg >= az_sorted(end)
    idx0 = order(end); idx1 = order(end); alpha = 0;
else
    insert = find(az_sorted >= yaw_deg,1);
    idx0 = order(insert-1);
    idx1 = order(insert);
    az0 = az_sorted(insert-1); az1 = az_sorted(insert);
    if az1 == az0
        alpha = 0;
    else
        alpha = (yaw_deg - az0) / (az1 - az0);
    end
end
% get HRIRs
[l0,r0] = get_hrir(dataset, idx0, el_idx);
[l1,r1] = get_hrir(dataset, idx1, el_idx);
left = (1-alpha)*l0 + alpha*l1;
right = (1-alpha)*r0 + alpha*r1;
used0 = az(idx0); used1 = az(idx1);
end

function [l,r] = get_hrir(dataset, az_idx, el_idx)
    hrir_l = dataset.hrir_l; hrir_r = dataset.hrir_r;
    if size(hrir_l,1) == numel(dataset.elevations) && size(hrir_l,2) == numel(dataset.azimuths)
        l = squeeze(hrir_l(el_idx, az_idx, :))';
        r = squeeze(hrir_r(el_idx, az_idx, :))';
    elseif size(hrir_l,1) == numel(dataset.azimuths) && size(hrir_l,2) == numel(dataset.elevations)
        l = squeeze(hrir_l(az_idx, el_idx, :))';
        r = squeeze(hrir_r(az_idx, el_idx, :))';
    else
        error('Unexpected HRIR layout');
    end
end
