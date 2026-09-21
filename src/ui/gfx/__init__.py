"""MLX-safe replacements for the Pygame convenience APIs flagged RED in
project-management/audits/pygame-mlx-api-matrix.md: image scaling, alpha
compositing, and text rendering. Everything here operates on raw pixel
buffers, mirroring what an MLX implementation would have to hand-roll on
top of mlx_get_data_addr / mlx_pixel_put instead of a library call.
"""
