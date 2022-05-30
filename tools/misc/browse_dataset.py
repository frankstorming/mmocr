# Copyright (c) OpenMMLab. All rights reserved.
import argparse
import os.path as osp

import mmcv
from mmcv import Config, DictAction

from mmocr.registry import DATASETS, VISUALIZERS
from mmocr.utils import register_all_modules


def parse_args():
    parser = argparse.ArgumentParser(description='Browse a dataset')
    parser.add_argument('config', help='Train config file path')
    parser.add_argument(
        '--output-dir',
        default=None,
        type=str,
        help='If there is no display interface, you can save it')
    parser.add_argument('--not-show', default=False, action='store_true')
    parser.add_argument(
        '--show-interval',
        type=float,
        default=2,
        help='The interval of show (s)')
    parser.add_argument(
        '--cfg-options',
        nargs='+',
        action=DictAction,
        help='Override some settings in the used config, the key-value pair '
        'in xxx=yyy format will be merged into config file. If the value to '
        'be overwritten is a list, it should be like key="[a,b]" or key=a,b '
        'It also allows nested list/tuple values, e.g. key="[(a,b),(c,d)]" '
        'Note that the quotation marks are necessary and that no white space '
        'is allowed.')
    args = parser.parse_args()
    return args


def main():

    args = parse_args()
    cfg = Config.fromfile(args.config)
    if args.cfg_options is not None:
        cfg.merge_from_dict(args.cfg_options)

    # register all modules in mmocr into the registries
    register_all_modules()

    dataset = DATASETS.build(cfg.train_dataloader.dataset)
    visualizer = VISUALIZERS.build(cfg.visualizer)

    progress_bar = mmcv.ProgressBar(len(dataset))
    for item in dataset:
        img = item['inputs'].permute(1, 2, 0).numpy()
        data_sample = item['data_sample'].numpy()
        img_path = osp.basename(item['data_sample'].img_path)
        out_file = osp.join(args.output_dir,
                            img_path) if args.output_dir is not None else None

        if img.ndim == 3 and img.shape[-1] == 3:
            img = img[..., [2, 1, 0]]  # bgr to rgb

        visualizer.add_datasample(
            name=osp.basename(img_path),
            image=img,
            gt_sample=data_sample,
            draw_pred=False,
            show=not args.not_show,
            wait_time=args.show_interval,
            out_file=out_file)

        progress_bar.update()


if __name__ == '__main__':
    main()