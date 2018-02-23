# Run with:
# vivado -mode batch -source ../scan_tx_phase.tcl

open_checkpoint top_route.dcp
set_property BITSTREAM.GENERAL.COMPRESS True [current_design]
set_property CLKOUT1_PHASE 0.0 [get_cells crg_main_mmcm]
write_bitstream top_0000.bit
set_property CLKOUT1_PHASE 22.5 [get_cells crg_main_mmcm]
write_bitstream top_0225.bit
set_property CLKOUT1_PHASE 45.0 [get_cells crg_main_mmcm]
write_bitstream top_0450.bit
set_property CLKOUT1_PHASE 67.5 [get_cells crg_main_mmcm]
write_bitstream top_0675.bit
set_property CLKOUT1_PHASE 90.0 [get_cells crg_main_mmcm]
write_bitstream top_0900.bit
set_property CLKOUT1_PHASE 112.5 [get_cells crg_main_mmcm]
write_bitstream top_1125.bit
set_property CLKOUT1_PHASE 135.0 [get_cells crg_main_mmcm]
write_bitstream top_1350.bit
set_property CLKOUT1_PHASE 157.5 [get_cells crg_main_mmcm]
write_bitstream top_1575.bit

set_property CLKOUT1_PHASE 180.0 [get_cells crg_main_mmcm]
write_bitstream top_1800.bit
set_property CLKOUT1_PHASE 202.5 [get_cells crg_main_mmcm]
write_bitstream top_2025.bit
set_property CLKOUT1_PHASE 225.0 [get_cells crg_main_mmcm]
write_bitstream top_2250.bit
set_property CLKOUT1_PHASE 247.5 [get_cells crg_main_mmcm]
write_bitstream top_2475.bit
set_property CLKOUT1_PHASE 270.0 [get_cells crg_main_mmcm]
write_bitstream top_2700.bit
set_property CLKOUT1_PHASE 292.5 [get_cells crg_main_mmcm]
write_bitstream top_2925.bit
set_property CLKOUT1_PHASE 315.0 [get_cells crg_main_mmcm]
write_bitstream top_3150.bit
set_property CLKOUT1_PHASE 337.5 [get_cells crg_main_mmcm]
write_bitstream top_3375.bit
quit
