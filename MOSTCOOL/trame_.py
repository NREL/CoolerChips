import sys
# export PYTHONPATH="${PYTHONPATH}:../Paraview/lib/python3.10/site-packages
sys.path.append("/Paraview/lib/python3.10/site-packages")
sys.path.append("/Paraview/lib/")

# from paraview.web import venv  # Available in PV 5.10-RC2+
# from paraview import simple
from paraview.simple import *

from pathlib import Path
from trame.app import get_server
from trame.widgets import vuetify, paraview, client
from trame.ui.vuetify import SinglePageLayout

# -----------------------------------------------------------------------------
# Trame setup
# -----------------------------------------------------------------------------

server = get_server(client_type = "vue2")
state, ctrl = server.state, server.controller

# Preload paraview modules onto server
paraview.initialize(server)

# -----------------------------------------------------------------------------
# ParaView code
# -----------------------------------------------------------------------------


def load_data(**kwargs):
    # CLI
    args, _ = server.cli.parse_known_args()

    # full_path = str(Path(args.data).resolve().absolute())
    # working_directory = str(Path(args.data).parent.resolve().absolute())

    # ParaView
    # simple.LoadState(
    #     full_path,
    #     data_directory=working_directory,
    #     restrict_to_data_directory=True,
    # )
    # view = simple.GetActiveView()
    # view.MakeRenderWindowInteractor(True)
    # simple.Render(view)

    #### disable automatic camera reset on 'Show'
    # simple._DisableFirstRenderCameraReset()

    # create a new 'CGNS Series Reader'
    solution_PythonPOD_Solidcgns = CGNSSeriesReader(registrationName='solution_PythonPOD_Solid.cgns', FileNames=['ThermalModel_datacenter/PythonPOD_Solid.cgns'])
    solution_PythonPOD_Solidcgns.Bases = ['Base']
    solution_PythonPOD_Solidcgns.Families = []
    solution_PythonPOD_Solidcgns.CellArrayStatus = []
    solution_PythonPOD_Solidcgns.FaceArrayStatus = []
    solution_PythonPOD_Solidcgns.PointArrayStatus = []
    solution_PythonPOD_Solidcgns.DataLocation = 'Cell Data'
    solution_PythonPOD_Solidcgns.LoadMesh = 1
    solution_PythonPOD_Solidcgns.LoadPatches = 0
    solution_PythonPOD_Solidcgns.DoublePrecisionMesh = 1
    solution_PythonPOD_Solidcgns.CacheMesh = 0
    solution_PythonPOD_Solidcgns.CacheConnectivity = 0
    solution_PythonPOD_Solidcgns.CreateEachSolutionAsBlock = 0
    solution_PythonPOD_Solidcgns.IgnoreFlowSolutionPointers = 0
    solution_PythonPOD_Solidcgns.UseUnsteadyPattern = 0
    solution_PythonPOD_Solidcgns.UnsteadySolutionStartTimestep = 0
    solution_PythonPOD_Solidcgns.Use3DVector = 1
    solution_PythonPOD_Solidcgns.IgnoreReaderTime = 0
    # Properties modified on solution_PythonPOD_Solidcgns
    solution_PythonPOD_Solidcgns.PointArrayStatus = ['Temperature']
    # get active view
    renderView1 = GetActiveViewOrCreate('RenderView')
    # show data in view
    solution_PythonPOD_SolidcgnsDisplay = Show(solution_PythonPOD_Solidcgns, renderView1, 'UnstructuredGridRepresentation')
    # trace defaults for the display properties.
    solution_PythonPOD_SolidcgnsDisplay.Selection = None
    solution_PythonPOD_SolidcgnsDisplay.Representation = 'Surface'
    solution_PythonPOD_SolidcgnsDisplay.ColorArrayName = [None, '']
    solution_PythonPOD_SolidcgnsDisplay.LookupTable = None
    solution_PythonPOD_SolidcgnsDisplay.MapScalars = 1
    solution_PythonPOD_SolidcgnsDisplay.MultiComponentsMapping = 0
    solution_PythonPOD_SolidcgnsDisplay.InterpolateScalarsBeforeMapping = 1
    solution_PythonPOD_SolidcgnsDisplay.UseNanColorForMissingArrays = 0
    solution_PythonPOD_SolidcgnsDisplay.Opacity = 1.0
    solution_PythonPOD_SolidcgnsDisplay.PointSize = 2.0
    solution_PythonPOD_SolidcgnsDisplay.LineWidth = 1.0
    solution_PythonPOD_SolidcgnsDisplay.RenderLinesAsTubes = 0
    solution_PythonPOD_SolidcgnsDisplay.RenderPointsAsSpheres = 0
    solution_PythonPOD_SolidcgnsDisplay.Interpolation = 'Gouraud'
    solution_PythonPOD_SolidcgnsDisplay.Specular = 0.0
    solution_PythonPOD_SolidcgnsDisplay.SpecularColor = [1.0, 1.0, 1.0]
    solution_PythonPOD_SolidcgnsDisplay.SpecularPower = 100.0
    solution_PythonPOD_SolidcgnsDisplay.Luminosity = 0.0
    solution_PythonPOD_SolidcgnsDisplay.Ambient = 0.0
    solution_PythonPOD_SolidcgnsDisplay.Diffuse = 1.0
    solution_PythonPOD_SolidcgnsDisplay.Roughness = 0.3
    solution_PythonPOD_SolidcgnsDisplay.Metallic = 0.0
    solution_PythonPOD_SolidcgnsDisplay.EdgeTint = [1.0, 1.0, 1.0]
    solution_PythonPOD_SolidcgnsDisplay.Anisotropy = 0.0
    solution_PythonPOD_SolidcgnsDisplay.AnisotropyRotation = 0.0
    solution_PythonPOD_SolidcgnsDisplay.BaseIOR = 1.5
    solution_PythonPOD_SolidcgnsDisplay.CoatStrength = 0.0
    solution_PythonPOD_SolidcgnsDisplay.CoatIOR = 2.0
    solution_PythonPOD_SolidcgnsDisplay.CoatRoughness = 0.0
    solution_PythonPOD_SolidcgnsDisplay.CoatColor = [1.0, 1.0, 1.0]
    solution_PythonPOD_SolidcgnsDisplay.SelectTCoordArray = 'None'
    solution_PythonPOD_SolidcgnsDisplay.SelectNormalArray = 'None'
    solution_PythonPOD_SolidcgnsDisplay.SelectTangentArray = 'None'
    solution_PythonPOD_SolidcgnsDisplay.Texture = None
    solution_PythonPOD_SolidcgnsDisplay.RepeatTextures = 1
    solution_PythonPOD_SolidcgnsDisplay.InterpolateTextures = 0
    solution_PythonPOD_SolidcgnsDisplay.SeamlessU = 0
    solution_PythonPOD_SolidcgnsDisplay.SeamlessV = 0
    solution_PythonPOD_SolidcgnsDisplay.UseMipmapTextures = 0
    solution_PythonPOD_SolidcgnsDisplay.ShowTexturesOnBackface = 1
    solution_PythonPOD_SolidcgnsDisplay.BaseColorTexture = None
    solution_PythonPOD_SolidcgnsDisplay.NormalTexture = None
    solution_PythonPOD_SolidcgnsDisplay.NormalScale = 1.0
    solution_PythonPOD_SolidcgnsDisplay.CoatNormalTexture = None
    solution_PythonPOD_SolidcgnsDisplay.CoatNormalScale = 1.0
    solution_PythonPOD_SolidcgnsDisplay.MaterialTexture = None
    solution_PythonPOD_SolidcgnsDisplay.OcclusionStrength = 1.0
    solution_PythonPOD_SolidcgnsDisplay.AnisotropyTexture = None
    solution_PythonPOD_SolidcgnsDisplay.EmissiveTexture = None
    solution_PythonPOD_SolidcgnsDisplay.EmissiveFactor = [1.0, 1.0, 1.0]
    solution_PythonPOD_SolidcgnsDisplay.FlipTextures = 0
    solution_PythonPOD_SolidcgnsDisplay.EdgeOpacity = 1.0
    solution_PythonPOD_SolidcgnsDisplay.BackfaceRepresentation = 'Follow Frontface'
    solution_PythonPOD_SolidcgnsDisplay.BackfaceAmbientColor = [1.0, 1.0, 1.0]
    solution_PythonPOD_SolidcgnsDisplay.BackfaceOpacity = 1.0
    solution_PythonPOD_SolidcgnsDisplay.Position = [0.0, 0.0, 0.0]
    solution_PythonPOD_SolidcgnsDisplay.Scale = [1.0, 1.0, 1.0]
    solution_PythonPOD_SolidcgnsDisplay.Orientation = [0.0, 0.0, 0.0]
    solution_PythonPOD_SolidcgnsDisplay.Origin = [0.0, 0.0, 0.0]
    solution_PythonPOD_SolidcgnsDisplay.CoordinateShiftScaleMethod = 'Always Auto Shift Scale'
    solution_PythonPOD_SolidcgnsDisplay.Pickable = 1
    solution_PythonPOD_SolidcgnsDisplay.Triangulate = 0
    solution_PythonPOD_SolidcgnsDisplay.UseShaderReplacements = 0
    solution_PythonPOD_SolidcgnsDisplay.ShaderReplacements = ''
    solution_PythonPOD_SolidcgnsDisplay.NonlinearSubdivisionLevel = 1
    solution_PythonPOD_SolidcgnsDisplay.MatchBoundariesIgnoringCellOrder = 0
    solution_PythonPOD_SolidcgnsDisplay.UseDataPartitions = 0
    solution_PythonPOD_SolidcgnsDisplay.OSPRayUseScaleArray = 'All Approximate'
    solution_PythonPOD_SolidcgnsDisplay.OSPRayScaleArray = 'Temperature'
    solution_PythonPOD_SolidcgnsDisplay.OSPRayScaleFunction = 'Piecewise Function'
    solution_PythonPOD_SolidcgnsDisplay.OSPRayMaterial = 'None'
    solution_PythonPOD_SolidcgnsDisplay.Assembly = 'Hierarchy'
    solution_PythonPOD_SolidcgnsDisplay.BlockSelectors = ['/']
    solution_PythonPOD_SolidcgnsDisplay.BlockColors = []
    solution_PythonPOD_SolidcgnsDisplay.BlockOpacities = []
    solution_PythonPOD_SolidcgnsDisplay.Orient = 0
    solution_PythonPOD_SolidcgnsDisplay.OrientationMode = 'Direction'
    solution_PythonPOD_SolidcgnsDisplay.SelectOrientationVectors = 'None'
    solution_PythonPOD_SolidcgnsDisplay.Scaling = 0
    solution_PythonPOD_SolidcgnsDisplay.ScaleMode = 'No Data Scaling Off'
    solution_PythonPOD_SolidcgnsDisplay.ScaleFactor = 0.09450000000000003
    solution_PythonPOD_SolidcgnsDisplay.SelectScaleArray = 'None'
    solution_PythonPOD_SolidcgnsDisplay.GlyphType = 'Arrow'
    solution_PythonPOD_SolidcgnsDisplay.UseGlyphTable = 0
    solution_PythonPOD_SolidcgnsDisplay.GlyphTableIndexArray = 'None'
    solution_PythonPOD_SolidcgnsDisplay.UseCompositeGlyphTable = 0
    solution_PythonPOD_SolidcgnsDisplay.UseGlyphCullingAndLOD = 0
    solution_PythonPOD_SolidcgnsDisplay.LODValues = []
    solution_PythonPOD_SolidcgnsDisplay.ColorByLODIndex = 0
    solution_PythonPOD_SolidcgnsDisplay.GaussianRadius = 0.004725000000000002
    solution_PythonPOD_SolidcgnsDisplay.ShaderPreset = 'Sphere'
    solution_PythonPOD_SolidcgnsDisplay.CustomTriangleScale = 3
    solution_PythonPOD_SolidcgnsDisplay.CustomShader = """ // This custom shader code define a gaussian blur
    // Please take a look into vtkSMPointGaussianRepresentation.cxx
    // for other custom shader examples
    //VTK::Color::Impl
    float dist2 = dot(offsetVCVSOutput.xy,offsetVCVSOutput.xy);
    float gaussian = exp(-0.5*dist2);
    opacity = opacity*gaussian;
    """
    solution_PythonPOD_SolidcgnsDisplay.Emissive = 0
    solution_PythonPOD_SolidcgnsDisplay.ScaleByArray = 0
    solution_PythonPOD_SolidcgnsDisplay.SetScaleArray = ['POINTS', 'Temperature']
    solution_PythonPOD_SolidcgnsDisplay.ScaleArrayComponent = ''
    solution_PythonPOD_SolidcgnsDisplay.UseScaleFunction = 1
    solution_PythonPOD_SolidcgnsDisplay.ScaleTransferFunction = 'Piecewise Function'
    solution_PythonPOD_SolidcgnsDisplay.OpacityByArray = 0
    solution_PythonPOD_SolidcgnsDisplay.OpacityArray = ['POINTS', 'Temperature']
    solution_PythonPOD_SolidcgnsDisplay.OpacityArrayComponent = ''
    solution_PythonPOD_SolidcgnsDisplay.OpacityTransferFunction = 'Piecewise Function'
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid = 'Grid Axes Representation'
    solution_PythonPOD_SolidcgnsDisplay.SelectionCellLabelBold = 0
    solution_PythonPOD_SolidcgnsDisplay.SelectionCellLabelColor = [0.0, 1.0, 0.0]
    solution_PythonPOD_SolidcgnsDisplay.SelectionCellLabelFontFamily = 'Arial'
    solution_PythonPOD_SolidcgnsDisplay.SelectionCellLabelFontFile = ''
    solution_PythonPOD_SolidcgnsDisplay.SelectionCellLabelFontSize = 18
    solution_PythonPOD_SolidcgnsDisplay.SelectionCellLabelItalic = 0
    solution_PythonPOD_SolidcgnsDisplay.SelectionCellLabelJustification = 'Left'
    solution_PythonPOD_SolidcgnsDisplay.SelectionCellLabelOpacity = 1.0
    solution_PythonPOD_SolidcgnsDisplay.SelectionCellLabelShadow = 0
    solution_PythonPOD_SolidcgnsDisplay.SelectionPointLabelBold = 0
    solution_PythonPOD_SolidcgnsDisplay.SelectionPointLabelColor = [1.0, 1.0, 0.0]
    solution_PythonPOD_SolidcgnsDisplay.SelectionPointLabelFontFamily = 'Arial'
    solution_PythonPOD_SolidcgnsDisplay.SelectionPointLabelFontFile = ''
    solution_PythonPOD_SolidcgnsDisplay.SelectionPointLabelFontSize = 18
    solution_PythonPOD_SolidcgnsDisplay.SelectionPointLabelItalic = 0
    solution_PythonPOD_SolidcgnsDisplay.SelectionPointLabelJustification = 'Left'
    solution_PythonPOD_SolidcgnsDisplay.SelectionPointLabelOpacity = 1.0
    solution_PythonPOD_SolidcgnsDisplay.SelectionPointLabelShadow = 0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes = 'Polar Axes Representation'
    solution_PythonPOD_SolidcgnsDisplay.ScalarOpacityFunction = None
    solution_PythonPOD_SolidcgnsDisplay.ScalarOpacityUnitDistance = 0.008075174922890045
    solution_PythonPOD_SolidcgnsDisplay.UseSeparateOpacityArray = 0
    solution_PythonPOD_SolidcgnsDisplay.OpacityArrayName = ['POINTS', 'Temperature']
    solution_PythonPOD_SolidcgnsDisplay.OpacityComponent = ''
    solution_PythonPOD_SolidcgnsDisplay.SelectMapper = 'Projected tetra'
    solution_PythonPOD_SolidcgnsDisplay.SamplingDimensions = [128, 128, 128]
    solution_PythonPOD_SolidcgnsDisplay.UseFloatingPointFrameBuffer = 1
    solution_PythonPOD_SolidcgnsDisplay.SelectInputVectors = [None, '']
    solution_PythonPOD_SolidcgnsDisplay.NumberOfSteps = 40
    solution_PythonPOD_SolidcgnsDisplay.StepSize = 0.25
    solution_PythonPOD_SolidcgnsDisplay.NormalizeVectors = 1
    solution_PythonPOD_SolidcgnsDisplay.EnhancedLIC = 1
    solution_PythonPOD_SolidcgnsDisplay.ColorMode = 'Blend'
    solution_PythonPOD_SolidcgnsDisplay.LICIntensity = 0.8
    solution_PythonPOD_SolidcgnsDisplay.MapModeBias = 0.0
    solution_PythonPOD_SolidcgnsDisplay.EnhanceContrast = 'Off'
    solution_PythonPOD_SolidcgnsDisplay.LowLICContrastEnhancementFactor = 0.0
    solution_PythonPOD_SolidcgnsDisplay.HighLICContrastEnhancementFactor = 0.0
    solution_PythonPOD_SolidcgnsDisplay.LowColorContrastEnhancementFactor = 0.0
    solution_PythonPOD_SolidcgnsDisplay.HighColorContrastEnhancementFactor = 0.0
    solution_PythonPOD_SolidcgnsDisplay.AntiAlias = 0
    solution_PythonPOD_SolidcgnsDisplay.MaskOnSurface = 1
    solution_PythonPOD_SolidcgnsDisplay.MaskThreshold = 0.0
    solution_PythonPOD_SolidcgnsDisplay.MaskIntensity = 0.0
    solution_PythonPOD_SolidcgnsDisplay.MaskColor = [0.5, 0.5, 0.5]
    solution_PythonPOD_SolidcgnsDisplay.GenerateNoiseTexture = 0
    solution_PythonPOD_SolidcgnsDisplay.NoiseType = 'Gaussian'
    solution_PythonPOD_SolidcgnsDisplay.NoiseTextureSize = 128
    solution_PythonPOD_SolidcgnsDisplay.NoiseGrainSize = 2
    solution_PythonPOD_SolidcgnsDisplay.MinNoiseValue = 0.0
    solution_PythonPOD_SolidcgnsDisplay.MaxNoiseValue = 0.8
    solution_PythonPOD_SolidcgnsDisplay.NumberOfNoiseLevels = 1024
    solution_PythonPOD_SolidcgnsDisplay.ImpulseNoiseProbability = 1.0
    solution_PythonPOD_SolidcgnsDisplay.ImpulseNoiseBackgroundValue = 0.0
    solution_PythonPOD_SolidcgnsDisplay.NoiseGeneratorSeed = 1
    solution_PythonPOD_SolidcgnsDisplay.CompositeStrategy = 'AUTO'
    solution_PythonPOD_SolidcgnsDisplay.UseLICForLOD = 0
    solution_PythonPOD_SolidcgnsDisplay.WriteLog = ''
    # init the 'Piecewise Function' selected for 'OSPRayScaleFunction'
    solution_PythonPOD_SolidcgnsDisplay.OSPRayScaleFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]
    solution_PythonPOD_SolidcgnsDisplay.OSPRayScaleFunction.UseLogScale = 0
    # init the 'Arrow' selected for 'GlyphType'
    solution_PythonPOD_SolidcgnsDisplay.GlyphType.TipResolution = 6
    solution_PythonPOD_SolidcgnsDisplay.GlyphType.TipRadius = 0.1
    solution_PythonPOD_SolidcgnsDisplay.GlyphType.TipLength = 0.35
    solution_PythonPOD_SolidcgnsDisplay.GlyphType.ShaftResolution = 6
    solution_PythonPOD_SolidcgnsDisplay.GlyphType.ShaftRadius = 0.03
    solution_PythonPOD_SolidcgnsDisplay.GlyphType.Invert = 0
    # init the 'Piecewise Function' selected for 'ScaleTransferFunction'
    solution_PythonPOD_SolidcgnsDisplay.ScaleTransferFunction.Points = [293.1458168718952, 0.0, 0.5, 0.0, 360.59209795705425, 1.0, 0.5, 0.0]
    solution_PythonPOD_SolidcgnsDisplay.ScaleTransferFunction.UseLogScale = 0
    # init the 'Piecewise Function' selected for 'OpacityTransferFunction'
    solution_PythonPOD_SolidcgnsDisplay.OpacityTransferFunction.Points = [293.1458168718952, 0.0, 0.5, 0.0, 360.59209795705425, 1.0, 0.5, 0.0]
    solution_PythonPOD_SolidcgnsDisplay.OpacityTransferFunction.UseLogScale = 0
    # init the 'Grid Axes Representation' selected for 'DataAxesGrid'
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.XTitle = 'X Axis'
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.YTitle = 'Y Axis'
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.ZTitle = 'Z Axis'
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.XTitleFontFamily = 'Arial'
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.XTitleFontFile = ''
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.XTitleBold = 0
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.XTitleItalic = 0
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.XTitleFontSize = 12
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.XTitleShadow = 0
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.XTitleOpacity = 1.0
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.YTitleFontFamily = 'Arial'
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.YTitleFontFile = ''
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.YTitleBold = 0
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.YTitleItalic = 0
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.YTitleFontSize = 12
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.YTitleShadow = 0
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.YTitleOpacity = 1.0
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.ZTitleFontFamily = 'Arial'
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.ZTitleFontFile = ''
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.ZTitleBold = 0
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.ZTitleItalic = 0
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.ZTitleFontSize = 12
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.ZTitleShadow = 0
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.ZTitleOpacity = 1.0
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.FacesToRender = 63
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.CullBackface = 0
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.CullFrontface = 1
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.ShowGrid = 0
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.ShowEdges = 1
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.ShowTicks = 1
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.LabelUniqueEdgesOnly = 1
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.AxesToLabel = 63
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.XLabelFontFamily = 'Arial'
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.XLabelFontFile = ''
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.XLabelBold = 0
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.XLabelItalic = 0
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.XLabelFontSize = 12
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.XLabelShadow = 0
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.XLabelOpacity = 1.0
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.YLabelFontFamily = 'Arial'
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.YLabelFontFile = ''
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.YLabelBold = 0
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.YLabelItalic = 0
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.YLabelFontSize = 12
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.YLabelShadow = 0
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.YLabelOpacity = 1.0
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.ZLabelFontFamily = 'Arial'
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.ZLabelFontFile = ''
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.ZLabelBold = 0
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.ZLabelItalic = 0
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.ZLabelFontSize = 12
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.ZLabelShadow = 0
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.ZLabelOpacity = 1.0
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.XAxisNotation = 'Mixed'
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.XAxisPrecision = 2
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.XAxisUseCustomLabels = 0
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.XAxisLabels = []
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.YAxisNotation = 'Mixed'
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.YAxisPrecision = 2
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.YAxisUseCustomLabels = 0
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.YAxisLabels = []
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.ZAxisNotation = 'Mixed'
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.ZAxisPrecision = 2
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.ZAxisUseCustomLabels = 0
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.ZAxisLabels = []
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.UseCustomBounds = 0
    solution_PythonPOD_SolidcgnsDisplay.DataAxesGrid.CustomBounds = [0.0, 1.0, 0.0, 1.0, 0.0, 1.0]
    # init the 'Polar Axes Representation' selected for 'PolarAxes'
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.Visibility = 0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.Translation = [0.0, 0.0, 0.0]
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.Scale = [1.0, 1.0, 1.0]
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.Orientation = [0.0, 0.0, 0.0]
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.EnableCustomBounds = [0, 0, 0]
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.CustomBounds = [0.0, 1.0, 0.0, 1.0, 0.0, 1.0]
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.EnableCustomRange = 0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.CustomRange = [0.0, 1.0]
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.AutoPole = 1
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.PolarAxisVisibility = 1
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.RadialAxesVisibility = 1
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.DrawRadialGridlines = 1
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.PolarArcsVisibility = 1
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.DrawPolarArcsGridlines = 1
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.NumberOfRadialAxes = 0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.DeltaAngleRadialAxes = 45.0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.NumberOfPolarAxes = 5
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.DeltaRangePolarAxes = 0.0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.CustomMinRadius = 1
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.MinimumRadius = 0.0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.CustomAngles = 1
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.MinimumAngle = 0.0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.MaximumAngle = 90.0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.RadialAxesOriginToPolarAxis = 1
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.PolarArcResolutionPerDegree = 0.2
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.Ratio = 1.0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.EnableOverallColor = 1
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.OverallColor = [1.0, 1.0, 1.0]
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.PolarAxisColor = [1.0, 1.0, 1.0]
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.PolarArcsColor = [1.0, 1.0, 1.0]
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.LastRadialAxisColor = [1.0, 1.0, 1.0]
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.SecondaryPolarArcsColor = [1.0, 1.0, 1.0]
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.SecondaryRadialAxesColor = [1.0, 1.0, 1.0]
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.PolarAxisTitleVisibility = 1
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.PolarAxisTitle = 'Radial Distance'
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.PolarAxisTitleLocation = 'Bottom'
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.PolarTitleOffset = [20.0, 20.0]
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.PolarLabelVisibility = 1
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.PolarLabelFormat = '%-#6.3g'
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.PolarLabelExponentLocation = 'Labels'
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.PolarLabelOffset = 10.0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.PolarExponentOffset = 5.0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.RadialTitleVisibility = 1
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.RadialTitleFormat = '%-#3.1f'
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.RadialTitleLocation = 'Bottom'
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.RadialTitleOffset = [20.0, 0.0]
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.RadialUnitsVisibility = 1
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.ScreenSize = 10.0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.PolarAxisTitleOpacity = 1.0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.PolarAxisTitleFontFamily = 'Arial'
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.PolarAxisTitleFontFile = ''
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.PolarAxisTitleBold = 0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.PolarAxisTitleItalic = 0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.PolarAxisTitleShadow = 0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.PolarAxisTitleFontSize = 12
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.PolarAxisLabelOpacity = 1.0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.PolarAxisLabelFontFamily = 'Arial'
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.PolarAxisLabelFontFile = ''
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.PolarAxisLabelBold = 0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.PolarAxisLabelItalic = 0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.PolarAxisLabelShadow = 0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.PolarAxisLabelFontSize = 12
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.LastRadialAxisTextOpacity = 1.0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.LastRadialAxisTextFontFamily = 'Arial'
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.LastRadialAxisTextFontFile = ''
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.LastRadialAxisTextBold = 0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.LastRadialAxisTextItalic = 0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.LastRadialAxisTextShadow = 0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.LastRadialAxisTextFontSize = 12
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.SecondaryRadialAxesTextOpacity = 1.0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.SecondaryRadialAxesTextFontFamily = 'Arial'
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.SecondaryRadialAxesTextFontFile = ''
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.SecondaryRadialAxesTextBold = 0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.SecondaryRadialAxesTextItalic = 0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.SecondaryRadialAxesTextShadow = 0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.SecondaryRadialAxesTextFontSize = 12
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.EnableDistanceLOD = 1
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.DistanceLODThreshold = 0.7
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.EnableViewAngleLOD = 1
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.ViewAngleLODThreshold = 0.7
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.SmallestVisiblePolarAngle = 0.5
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.PolarTicksVisibility = 1
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.ArcTicksOriginToPolarAxis = 1
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.TickLocation = 'Both'
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.AxisTickVisibility = 1
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.AxisMinorTickVisibility = 0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.AxisTickMatchesPolarAxes = 1
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.DeltaRangeMajor = 1.0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.DeltaRangeMinor = 0.5
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.ArcTickVisibility = 1
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.ArcMinorTickVisibility = 0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.ArcTickMatchesRadialAxes = 1
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.DeltaAngleMajor = 10.0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.DeltaAngleMinor = 5.0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.TickRatioRadiusSize = 0.02
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.PolarAxisMajorTickSize = 0.0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.PolarAxisTickRatioSize = 0.3
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.PolarAxisMajorTickThickness = 1.0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.PolarAxisTickRatioThickness = 0.5
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.LastRadialAxisMajorTickSize = 0.0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.LastRadialAxisTickRatioSize = 0.3
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.LastRadialAxisMajorTickThickness = 1.0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.LastRadialAxisTickRatioThickness = 0.5
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.ArcMajorTickSize = 0.0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.ArcTickRatioSize = 0.3
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.ArcMajorTickThickness = 1.0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.ArcTickRatioThickness = 0.5
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.Use2DMode = 0
    solution_PythonPOD_SolidcgnsDisplay.PolarAxes.UseLogAxis = 0
    # reset view to fit data
    # get the bounds of the object
    bounds = solution_PythonPOD_Solidcgns.GetDataInformation().GetBounds()
    center = [(bounds[1] + bounds[0]) / 2.0, (bounds[3] + bounds[2]) / 2.0, (bounds[5] + bounds[4]) / 2.0]

    # set the center of rotation to the center of the object
    renderView1.CenterOfRotation = center

    # reset the camera to the new center
    renderView1.ResetCamera()
    # get the material library
    materialLibrary1 = GetMaterialLibrary()
    # update the view to ensure updated data information
    renderView1.Update()
    # set scalar coloring
    ColorBy(solution_PythonPOD_SolidcgnsDisplay, ('POINTS', 'Temperature'))
    # rescale color and/or opacity maps used to include current data range
    solution_PythonPOD_SolidcgnsDisplay.RescaleTransferFunctionToDataRange(True, False)
    # show color bar/color legend
    solution_PythonPOD_SolidcgnsDisplay.SetScalarBarVisibility(renderView1, True)
    # get color transfer function/color map for 'Temperature'
    temperatureLUT = GetColorTransferFunction('Temperature')
    # get opacity transfer function/opacity map for 'Temperature'
    temperaturePWF = GetOpacityTransferFunction('Temperature')
    # get 2D transfer function for 'Temperature'
    temperatureTF2D = GetTransferFunction2D('Temperature')
    #================================================================
    # addendum: following script captures some of the application
    # state to faithfully reproduce the visualization during playback
    #================================================================
    # get layout
    layout1 = GetLayout()
    #--------------------------------
    # saving layout sizes for layouts
    # layout/tab size in pixels
    layout1.SetSize(1517, 753)
    #-----------------------------------
    # saving camera placements for views
    # current camera placement for renderView1
    renderView1.CameraPosition = [1.0767156547890369, 1.8095092029905198, 2.0889245420682934]
    renderView1.CameraFocalPoint = [0.40289488983154315, 0.5249311523437501, 0.6909018554687502]
    renderView1.CameraViewUp = [-0.03681709391361909, 0.7446302761159348, -0.6664609917221431]
    renderView1.CameraParallelScale = 0.5214187408880739

    renderView1.MakeRenderWindowInteractor(True)
    Render(renderView1)

    # HTML
    with SinglePageLayout(server) as layout:
        layout.icon.click = ctrl.view_reset_camera
        layout.title.set_text("Server Board Thermal Profile")

        with layout.content:
            with vuetify.VContainer(fluid=True, classes="pa-0 fill-height"):
                html_view = paraview.VtkLocalView(renderView1)
                ctrl.view_reset_camera = html_view.reset_camera
                ctrl.view_update = html_view.update


ctrl.on_server_ready.add(load_data)

# -----------------------------------------------------------------------------
# GUI
# -----------------------------------------------------------------------------

state.trame__title = "Server Board Thermal Profile"

with SinglePageLayout(server) as layout:
    layout.icon.click = ctrl.view_reset_camera
    layout.title.set_text("Server Board Thermal Profile")

    with layout.content:
        with vuetify.VContainer(fluid=True, classes="pa-0 fill-height"):
            client.Loading("Loading state")


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    # server.cli.add_argument("--data", help="Path to state file", dest="data")
    server.start()