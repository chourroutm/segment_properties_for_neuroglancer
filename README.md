# segment_properties

This script creates a JSON [`segment_properties/info`](https://github.com/google/neuroglancer/blob/master/src/datasource/precomputed/segment_properties.md) file for [the Neuroglancer precomputed format](https://github.com/google/neuroglancer/blob/master/src/datasource/precomputed/volume.md) (for segmentation types only).

Please note that you will still need to rename the output file and to append `"segment_properties":"segment_properties"` to the `info` file of the volume.
