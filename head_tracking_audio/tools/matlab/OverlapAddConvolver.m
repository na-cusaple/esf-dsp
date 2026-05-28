classdef OverlapAddConvolver < handle
    % OverlapAddConvolver MATLAB implementation mirroring Python version
    properties
        block_size
        hrir_l
        hrir_r
        fft_size
        hrir_l_fft
        hrir_r_fft
        overlap_len
        overlap_l
        overlap_r
    end
    methods
        function obj = OverlapAddConvolver(hrir_l, hrir_r, block_size)
            obj.block_size = double(block_size);
            obj.hrir_l = double(hrir_l(:)');
            obj.hrir_r = double(hrir_r(:)');
            obj.fft_size = 2^nextpow2(obj.block_size + numel(obj.hrir_l) - 1);
            obj.hrir_l_fft = fft(obj.hrir_l, obj.fft_size);
            obj.hrir_r_fft = fft(obj.hrir_r, obj.fft_size);
            obj.overlap_len = obj.fft_size - obj.block_size;
            obj.overlap_l = zeros(1, obj.overlap_len);
            obj.overlap_r = zeros(1, obj.overlap_len);
        end

        function [out_l, out_r] = process(obj, block)
            block = double(block(:)');
            if numel(block) ~= obj.block_size
                % pad or truncate
                tmp = zeros(1, obj.block_size);
                n = min(numel(block), obj.block_size);
                tmp(1:n) = block(1:n);
                block = tmp;
            end
            fft_in = zeros(1, obj.fft_size);
            fft_in(1:obj.block_size) = block;
            X = fft(fft_in);
            y_l = ifft(X .* obj.hrir_l_fft, obj.fft_size);
            y_r = ifft(X .* obj.hrir_r_fft, obj.fft_size);
            y_l = real(y_l);
            y_r = real(y_r);
            out_l = y_l(1:obj.block_size);
            out_r = y_r(1:obj.block_size);
            add_len = min(obj.overlap_len, obj.block_size);
            if add_len > 0
                out_l(1:add_len) = out_l(1:add_len) + obj.overlap_l(1:add_len);
                out_r(1:add_len) = out_r(1:add_len) + obj.overlap_r(1:add_len);
            end
            % store tail
            obj.overlap_l = y_l(obj.block_size+1:obj.block_size+obj.overlap_len);
            obj.overlap_r = y_r(obj.block_size+1:obj.block_size+obj.overlap_len);
        end
    end
end
