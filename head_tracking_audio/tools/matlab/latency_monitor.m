classdef LatencyMonitor < handle
    properties
        window = 200;
        samples = [];
        queue_age = [];
        uart_delay = [];
        _start = [];
    end
    methods
        function obj = LatencyMonitor(window)
            if nargin>0
                obj.window = window;
            end
            obj.samples = zeros(0,2);
            obj.queue_age = [];
            obj.uart_delay = [];
        end

        function start_callback(obj)
            obj._start = tic;
        end

        function end_callback(obj, frames, sample_rate)
            if isempty(obj._start)
                return
            end
            elapsed = toc(obj._start);
            budget = double(frames)/double(sample_rate);
            obj.samples(end+1,:) = [elapsed, budget];
            if size(obj.samples,1) > obj.window
                obj.samples(1,:) = [];
            end
            obj._start = [];
        end

        function record_queue_age(obj, age_sec)
            if isempty(age_sec), return; end
            obj.queue_age(end+1) = age_sec;
            if numel(obj.queue_age) > obj.window
                obj.queue_age(1) = [];
            end
        end

        function record_uart_delay(obj, delay_sec)
            if isempty(delay_sec), return; end
            obj.uart_delay(end+1) = delay_sec;
            if numel(obj.uart_delay) > obj.window
                obj.uart_delay(1) = [];
            end
        end

        function s = stats(obj)
            if isempty(obj.samples) && isempty(obj.queue_age) && isempty(obj.uart_delay)
                s = [];
                return;
            end
            s = struct();
            if ~isempty(obj.samples)
                elapsed = obj.samples(:,1);
                budget = obj.samples(:,2);
                s.avg_ms = 1000*mean(elapsed);
                s.max_ms = 1000*max(elapsed);
                s.overruns = sum(elapsed > budget & budget>0);
                s.budget_ms = 1000*mean(budget);
            end
            if ~isempty(obj.queue_age)
                s.queue_age_avg_ms = 1000*mean(obj.queue_age);
                s.queue_age_max_ms = 1000*max(obj.queue_age);
            end
            if ~isempty(obj.uart_delay)
                s.uart_delay_avg_ms = 1000*mean(obj.uart_delay);
                s.uart_delay_max_ms = 1000*max(obj.uart_delay);
            end
        end
    end
end
