function qn = normalize_quat(q)
% q as 1x4 vector [w x y z]
    q = double(q);
    n = norm(q);
    if n <= 0
        qn = [1 0 0 0];
    else
        qn = q ./ n;
    end
end

function [roll,pitch,yaw] = quat_to_euler(q)
    q = normalize_quat(q);
    qw = q(1); qx = q(2); qy = q(3); qz = q(4);
    sinr_cosp = 2*(qw*qx + qy*qz);
    cosr_cosp = 1 - 2*(qx*qx + qy*qy);
    roll = atan2(sinr_cosp, cosr_cosp);
    sinp = 2*(qw*qy - qz*qx);
    if abs(sinp) >= 1
        pitch = sign(sinp) * pi/2;
    else
        pitch = asin(sinp);
    end
    siny_cosp = 2*(qw*qz + qx*qy);
    cosy_cosp = 1 - 2*(qy*qy + qz*qz);
    yaw = atan2(siny_cosp, cosy_cosp);
    % return degrees to match python
    roll = rad2deg(roll); pitch = rad2deg(pitch); yaw = rad2deg(yaw);
end

function qout = nlerp_quat(qprev, qcurr, alpha)
    qprev = normalize_quat(qprev);
    qcurr = normalize_quat(qcurr);
    d = dot(qprev, qcurr);
    if d < 0
        qcurr = -qcurr;
    end
    qtemp = (1-alpha)*qprev + alpha*qcurr;
    qout = normalize_quat(qtemp);
end
