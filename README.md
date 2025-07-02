# spectralassistant

<p align="center">
  <img src="assets/mads.png" alt="Mads Logo" />
</p>


## Key Features

- [**Identifying the main component information of the substance**](#polarization-demosaicing)
  - Both Monochrome/Color Polarization image sensors (*e.g.*, IMX250MZR / MYR) are supported.
- [**Matching substance related database**](#analysis-of-stokes-vector)
  - Obtain Stokes vector from images captured with a polarization camera or custom setup.
  - Convert Stokes vector to meaningful parameters, such as DoLP, AoLP.
- [**Analysis of massive data**](#analysis-of-mueller-matrix)
  - Provide basic Mueller matrix elements, such as polarizer, retarder, and rotator.
  - Obtain Mueller matrix from images captured under a variety of polarimetric conditions by using a least-squares method.
- [**Collaboration with Multi-agent**](#visualizing-polarimetric-images)
  - Apply colormap to polarization images, such as DoLP, AoLP, ToP, and CoP.
  - Visualize the Mueller matrix image in grid form.
- [**Symbolic Stokes-Mueller computation**](#symbolic-stokes-mueller-computation)
  - Symbolic calculation of the Stokes vector and Mueller matrix to understand complex combinations of optical elements.

## Dependencies and Installation

- Numpy
- OpenCV
- matplotlib
- SymPy (optional)

```sh
pip install polanalyser
```

## Polarization Image Dataset

Dataset of images captured by a polarization camera (FLIR, BFS-U3-51S5P-C) is available. You can use these images to learn how to analyze polarization images.

[**[Click here to download the dataset (Google Drive)]**](https://drive.google.com/drive/folders/1vCe9N05to5_McvwyDqxTmLIKz7vRzmbX?usp=sharing)

[![](documents/dataset_overview.png)](https://drive.google.com/drive/folders/1vCe9N05to5_McvwyDqxTmLIKz7vRzmbX?usp=sharing)

## Usage

### Polarization demosaicing

Demosaic raw polarization image captured with a polarization sensor (*e.g.*, [IMX250MZR / MYR](https://www.sony-semicon.com/en/products/is/industry/polarization.html)).

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="documents/demosaicing_dark.png">
  <source media="(prefers-color-scheme: light)" srcset="documents/demosaicing_light.png">
  <img alt="demosaicing" src="documents/demosaicing_light.png">
</picture>

```python
import cv2
import polanalyser as pa

img_raw = cv2.imread("dataset/dragon.png", 0)

img_000, img_045, img_090, img_135 = pa.demosaicing(img_raw, pa.COLOR_PolarMono)
# img_000, img_045, img_090, img_135 = pa.demosaicing(img_raw, pa.COLOR_PolarRGB)
```

### Analysis of Stokes vector

[**Stokes vector**](https://en.wikipedia.org/wiki/Stokes_parameters) describes the polarization states. We can measure these values by using a *linear polarizer* (To measure the circular polarization $s_3$, we also need to use a *retarder*).

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="documents/stokes_setup_dark.png">
  <source media="(prefers-color-scheme: light)" srcset="documents/stokes_setup_light.png">
  <img alt="Stokes setup" src="documents/stokes_setup_light.png">
</picture>

  <source media="(prefers-color-scheme: dark)" srcset="documents/mueller_setup_dark.png">
  <source media="(prefers-color-scheme: light)" srcset="documents/mueller_setup_light.png">
  <img alt="Mueller setup" src="documents/mueller_setup_light.png">
</picture>

$I$ denotes the intensity of the unpolarized light source. $`\mathbf{M}_\textrm{PSG}`$ and $`\mathbf{M}_\textrm{PSA}`$ represent the Polarization state generator and analyzer (PSG and PSA) in Mueller matrix form. PSG and PSA are commonly composed of the basic optical elements (i.e., linear polarizer and retarder).
The detector measures the intensity $f$ expressed by $`f = [ \mathbf{M}_\textrm{PSA} \mathbf{M} \mathbf{M}_\textrm{PSG} I]_{00}`$. $[...]_{00}$ extracts the (0, 0) component of the matrix.

Measuring $f$ by changing many combinations of $`\mathbf{M}_\textrm{PSG}`$ and $`\mathbf{M}_\textrm{PSA}`$ can estimate the unknown Mueller matrix $`\mathbf{M}`$ with a linear least-squares method.

The following code shows the example to estimate the 3x3 Mueller matrix image.

```python
import polanalyser as pa

# Read 16 images and Mueller matrices of PSG and PSA
filepath = "dataset/toy_example_3x3_pc"
images, props = pa.imreadMultiple(filepath)
print(images.shape)  # (16, 2048, 2448)
mm_psg = props["mueller_psg"] # (16, 3, 3)
mm_psa = props["mueller_psa"] # (16, 3, 3)

# Calculate Mueller matrix image
img_mueller = pa.calcMueller(images, mm_psg, mm_psa)
print(img_mueller.shape)  # (2048, 2448, 3, 3)
```

![](documents/mueller_various.jpg)


### Visualizing polarimetric images

### Stokes vector visualization

Polanalyser provides functions to visualize Stokes vector images, such as AoLP, DoLP, ToP (Type of Polarization), and CoP (Chirality of Polarization). The color mapping is designed based on the relevant papers [[Wilkie and Weidlich, SCCG2010]](https://dl.acm.org/doi/10.1145/1925059.1925070), [[Baek+, SIGGRAPH2020]](http://vclab.kaist.ac.kr/siggraph2020/index.html), [[Jeon+, CVPR2024]](https://eschoi.com/SPDataset/). Note that this mapping is slightly different from the original papers.

```python
# Example of visualization functions
img_aolp_vis = pa.applyColorToAoLP(img_aolp)
img_dolp_vis = pa.applyColorToDoP(img_dolp)
img_top_vis = pa.applyColorToToP(img_ellipticity_angle, img_dop)
img_cop_vis = pa.applyColorToCoP(img_ellipticity_angle)
```

Here is an example of visualizing the Stokes vector images. The stokes image is borrowed from the spectro-polarimetric dataset [[Jeon+, CVPR2024]](https://huggingface.co/datasets/jyj7913/spectro-polarimetric).

|||||
|:-:|:-:|:-:|:-:|
| s0 | s1 | s2 | s3 |
|![](documents/visualization/color.jpeg)|![](documents/visualization/s1.jpeg)|![](documents/visualization/s2.jpeg)|![](documents/visualization/s3.jpeg)|
| DoLP | AoLP | AoLP (light) | AoLP (dark) |
|![](documents/visualization/dolp.jpeg)|![](documents/visualization/aolp.jpeg)|![](documents/visualization/aolp_light.jpeg)|![](documents/visualization/aolp_dark.jpeg)|
| DoP | DoCP | ToP | CoP |
|![](documents/visualization/dop.jpeg)|![](documents/visualization/docp.jpeg)|![](documents/visualization/top.jpeg)|![](documents/visualization/cop.jpeg)|

In AoLP visualization, Polanalyser provides three types of AoLP visualization: AoLP, AoLP (light), and AoLP (dark). For more details, [see the wiki page](https://github.com/elerac/polanalyser/wiki/How-to-Visualizing-the-AoLP-Image).

### Mueller matrix visualization

Polanalyser provides functions to apply a colormap and make a 3x3 or 4x4 grid to visualize the Mueller matrix image.

Before visualizing the Mueller matrix image, we need to normalize the Mueller matrix. Here are three possible options, each with pros and cons. You need to choose the appropriate normalization method according to the purpose of the visualization and the chosen colormap.

```python
# Normalize Mueller matrix image
# img_mueller: (H, W, 3, 3)

# Option 1: Normalize by the maximum value
# Pros: Show values linearly
# Cons: The small values may not be visible
img_mueller_maxnorm = img_mueller / np.abs(img_mueller).max()  

# Option 2: Gamma correction
# Pros: Enhance the small values
# Cons: The large values become saturated
img_mueller_gamma = pa.gammaCorrection(img_mueller_maxnorm)  

# Option 3: m00 norm (scale by m00 value of each pixel)
# Pros: Visualizes polarization components ratio independently of the intensity
# Cons: m00 becomes 1, and cannot represent the absolute intensity
img_mueller_m00norm = img_mueller / img_mueller[..., 0, 0][..., None, None]  
```

After normalizing the Mueller matrix image, we can apply a colormap and make a grid to visualize the Mueller matrix image.

```python
# Apply colormap and make grid
img_mueller_norm_vis = pa.applyColorMap(img_mueller_maxnorm, "RdBu", -1, 1)  # (H, W, 3, 3, 3)
img_mueller_norm_vis_grid = pa.makeGridMueller(img_mueller_maxnorm_vis) # (H*3, W*3, 3)
```

| Max norm | Max norm + Gamma | m00 norm |
|:--------------:|:--------------:|:--------------:|
|![](documents/visualization/mueller_maxnorm_vis_grid.jpeg)|![](documents/visualization/mueller_gamma_vis_grid.jpeg)|![](documents/visualization/mueller_m00norm_vis_grid.jpeg)|

### Symbolic Stokes-Mueller computation

This feature supports the symbolic computation of the Stokes vector and Mueller matrix powered by SymPy. This feature is particularly useful for understanding the effects of complex combinations of optical elements. 

Here are examples of Malus's law and an ellipsometer. We can symbolically obtain the intensity of light passing through the sequence of optical elements without tedious calculations by hand.

```python
from sympy import symbols, simplify
import polanalyser.sympy as pas

theta = symbols("theta", real=True)

# Example 1: Malus's law
M_L1 = pas.polarizer(0)
M_L2 = pas.polarizer(theta)
f = (M_L2 @ M_L1)[0, 0]  
print(simplify(f))  
# 0.5*cos(theta)**2

# Example 2: Ellipsometer [Azzam+, 1978][Baek+, 2020]
M = pas.mueller()  # Symbolic Mueller matrix
I = 1.0
M_PSG = pas.qwp(theta) @ pas.polarizer(0)
M_PSA = pas.polarizer(0) @ pas.qwp(5 * theta)
f = (M_PSA @ M @ M_PSG * I)[0, 0] 
print(simplify(f))  
# 0.25*m00 + 0.25*m10*cos(10*theta)**2 + 0.125*m20*sin(20*theta) - 0.25*m30*sin(10*theta) + 0.25*(m01 + m11*cos(10*theta)**2 + m21*sin(20*theta)/2 - m31*sin(10*theta))*cos(2*theta)**2 + 0.25*(m02 + m12*cos(10*theta)**2 + m22*sin(20*theta)/2 - m32*sin(10*theta))*sin(2*theta)*cos(2*theta) + 0.25*(m03 + m13*cos(10*theta)**2 + m23*sin(20*theta)/2 - m33*sin(10*theta))*sin(2*theta)
```

## Notations

Please refer to the [notations.md](documents/notations.md) for the definition of the Stokes vector and Mueller matrix used in Polanalyser.


## Citation

If you find Polanalyser useful, please consider citing as follows:

```bibtex
@software{maeda2019polanalyser,
  author = {Ryota Maeda},
  title = {Polanalyser: Polarization Image Analysis Tool},
  url = {https://github.com/elerac/polanalyser},
  year = {2019},
}
```

## Related Project

If you like Polanalyser, you are also interested in the following paper.

<<<<<<< HEAD
- Ryota Maeda, Shinsaku Hiura, **Polarimetric Light Transport Analysis for Specular Inter-reflection**,  IEEE Transactions on Computational Imaging, 2024. [[Project Page]](https://elerac.github.io/projects/PolarimetricInterreflection/)
=======
- Ryota Maeda, Shinsaku Hiura, **Polarimetric Light Transport Analysis for Specular Inter-reflection**,  IEEE Transactions on Computational Imaging, 2024. [[Project Page]](https://elerac.github.io/projects/PolarimetricInterreflection/)
>>>>>>> github_publish
