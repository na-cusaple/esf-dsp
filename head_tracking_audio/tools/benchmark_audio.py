import argparse
import time

from python_host.dsp.hrtf_loader import load_cipic_mat
from python_host.dsp.hrtf_selector import select_hrir
from python_host.audio.buffer_manager import AudioFileBuffer, OverlapAddConvolver
from python_host.config.audio_config import HRTF_SAMPLE_RATE


def _parse_block_sizes(value):
    sizes = []
    for part in value.split(","):
        part = part.strip()
        if part:
            sizes.append(int(part))
    return sizes


def benchmark(input_wav, hrtf_mat, yaw, pitch, blocks, block_sizes, hrtf_sample_rate=None):
    audio_buffer = AudioFileBuffer.from_wav(input_wav)
    dataset = load_cipic_mat(
        hrtf_mat,
        target_sample_rate=audio_buffer.sample_rate,
        source_sample_rate=hrtf_sample_rate,
    )
    hrir_l, hrir_r, used = select_hrir(dataset, yaw, pitch)

    print("Using HRIR angles:", used)
    print("Sample rate:", audio_buffer.sample_rate)

    for block_size in block_sizes:
        convolver = OverlapAddConvolver(hrir_l, hrir_r, block_size)
        audio_buffer.position = 0

        start = time.perf_counter()
        for _ in range(blocks):
            block = audio_buffer.get_block(block_size)
            convolver.process(block)
        elapsed = time.perf_counter() - start

        avg_ms = 1000.0 * elapsed / float(blocks)
        budget_ms = 1000.0 * float(block_size) / float(audio_buffer.sample_rate)
        headroom = budget_ms - avg_ms

        print(
            "block %4d | avg %.2f ms | budget %.2f ms | headroom %.2f ms"
            % (block_size, avg_ms, budget_ms, headroom)
        )


def main():
    parser = argparse.ArgumentParser(description="Benchmark overlap-add convolution")
    parser.add_argument("--input", required=True, help="Input mono wav")
    parser.add_argument("--hrtf", required=True, help="CIPIC .mat file path")
    parser.add_argument("--yaw", type=float, default=0.0)
    parser.add_argument("--pitch", type=float, default=0.0)
    parser.add_argument("--blocks", type=int, default=300)
    parser.add_argument("--block-sizes", default="1024,512,256,128")
    parser.add_argument("--hrtf-sr", type=int, default=HRTF_SAMPLE_RATE)
    args = parser.parse_args()

    block_sizes = _parse_block_sizes(args.block_sizes)
    benchmark(
        args.input,
        args.hrtf,
        args.yaw,
        args.pitch,
        args.blocks,
        block_sizes,
        hrtf_sample_rate=args.hrtf_sr,
    )


if __name__ == "__main__":
    main()
