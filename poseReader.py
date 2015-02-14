import maya.cmds as cmds

#Declare Selection for constraints
constSel = cmds.ls(sl=1)

#Create Locators and set position and override colours 
baseLoc = cmds.spaceLocator(n = "base_loc")[0]
targetLoc = cmds.spaceLocator(n = "target_loc")[0]
constLoc = cmds.spaceLocator(n = "const_loc")[0]
poseLoc = cmds.spaceLocator(n = "pose_loc")[0]
cmds.xform(targetLoc,t=(0,2,0))
cmds.xform(constLoc,t=(1,2,0))
cmds.xform(poseLoc,t=(1,2,0))
poseRLoc = [baseLoc,targetLoc,constLoc]
for prl in poseRLoc:
    cmds.setAttr(prl+"Shape.overrideEnabled", 1)
    cmds.setAttr(prl+"Shape.overrideColor", 17)

#Create Coneshape and set xfrom
csl1 = cmds.curve(d = 1, p =[(0,0,0),(0,1,-1)],k = [0, 1], n = "coneLine1")
csl2 = cmds.curve(d = 1, p =[(0,0,0),(1,1,0)],k = [0, 1], n = "coneLine2")
csl3 = cmds.curve(d = 1, p =[(0,0,0),(0,1,1)],k =[0,1], n = "coneLine3")
csl4 = cmds.curve(d = 1, p =[(0,0,0),(-1,1,0)],k =[0,1], n = "coneLine4")
csl5 = cmds.curve(d = 1, p =[(0,0,0),(-0.707106,1,0.707106)],k =[0,1], n = "coneLine5")
csl6 = cmds.curve(d = 1, p =[(0,0,0),(0.707106,1,0.707106)],k =[0,1], n = "coneLine6")
csl7 = cmds.curve(d = 1, p =[(0,0,0),(0.707106,1,-0.707106)],k =[0,1], n = "coneLine7")
csl8 = cmds.curve(d = 1, p =[(0,0,0),(-0.707106,1,-0.707106)],k =[0,1], n = "coneLine8")
csc1 = cmds.circle(c= (0,1,0),nr = (0,1,0), sw = 360, r = 1, s = 8,ch = 0)
poseRcs = [csl1,csl2,csl3,csl4,csl5,csl6,csl7,csl8,csc1]
for prcs in poseRcs:
    cmds.setAttr((cmds.listRelatives(prcs, type = 'shape')[0] + ".overrideEnabled"),1)
    cmds.setAttr((cmds.listRelatives(prcs, type = 'shape')[0] + ".overrideColor"),18)
lineShapes = [csl1,csl2,csl3,csl4,csl5,csl6,csl7,csl8]
for lShp in lineShapes:
    cmds.parent((cmds.listRelatives(lShp, type = 'shape')),csc1,s=1,r=1)
    cmds.delete(lShp)
cmds.rename(csc1,"cone_01")

#Create Cone Adjustment Handle
coneAdj = cmds.curve(d=1, p=[(-1,0,1),(1,0,1),(1,0,-1),(-1,0,-1),(-1,0,1)], k=[0,1,2,3,4], n= "cone_CTRL")
cmds.setAttr((cmds.listRelatives(coneAdj, type="shape")[0] +".overrideEnabled"),1)
cmds.setAttr((cmds.listRelatives(coneAdj, type="shape")[0] +".overrideColor"),14)
cmds.xform(coneAdj,ro=(90,0,0))
cmds.xform(coneAdj,s=(0.333,0.333,0.333))
cmds.xform(coneAdj,t=(1,2,0))
cmds.makeIdentity(coneAdj,a=1, r=1, s=1)
cmds.connectAttr(coneAdj + '.translateX',poseLoc + '.translateX')
cmds.connectAttr(coneAdj + '.translateY',poseLoc + '.translateY')
cmds.setAttr(poseLoc + '.visibility',0)

#Connect Cone Adjustment Translate to Scale of Cone Shape
cmds.connectAttr('cone_CTRL.translateX', 'cone_01.scaleX')
cmds.connectAttr('cone_CTRL.translateX', 'cone_01.scaleZ')
cmds.connectAttr('cone_CTRL.translateY', 'cone_01.scaleY')


#Group all viewable thingies
grp = cmds.group("cone_01","cone_CTRL",baseLoc,targetLoc,constLoc,poseLoc,n="poseReader_grp")
cmds.move(0,0,0,grp + '.scalePivot', grp + '.rotatePivot')
cmds.setAttr(grp + '.rotateZ', -90)
cmds.makeIdentity(grp,a=1,r=1)
cmds.setAttr('cone_CTRL.translateZ',l=1,k=0,cb=0)
cmds.setAttr('cone_CTRL.rotateX',l=1,k=0,cb=0)
cmds.setAttr('cone_CTRL.rotateY',l=1,k=0,cb=0)
cmds.setAttr('cone_CTRL.rotateZ',l=1,k=0,cb=0)
cmds.setAttr('cone_CTRL.scaleX',l=1,k=0,cb=0)
cmds.setAttr('cone_CTRL.scaleY',l=1,k=0,cb=0)
cmds.setAttr('cone_CTRL.scaleZ',l=1,k=0,cb=0)
cmds.addAttr('poseReader_grp', ln = 'outputAngle', at="float", r=1, h=0, k=0)

#Decompose Matrix on Locators
locators = [baseLoc, targetLoc, constLoc, poseLoc]
for locs in locators:
    dcm = cmds.shadingNode('decomposeMatrix', n=locs + '_dcMatrix', asUtility=1)
    cmds.connectAttr((cmds.listRelatives(locs, type='shape')[0] + '.worldMatrix[0]'), dcm + '.inputMatrix')
    
#Find Angle using PMA
targetPMA = cmds.shadingNode('plusMinusAverage', n="target_PMA", asUtility=1)
constPMA = cmds.shadingNode('plusMinusAverage', n="const_PMA", asUtility=1)
posePMA = cmds.shadingNode('plusMinusAverage', n="pose_PMA", asUtility=1)
cmds.setAttr(targetPMA + '.operation',2)
cmds.setAttr(constPMA + '.operation',2)
cmds.setAttr(posePMA + '.operation',2)
cmds.connectAttr('target_loc_dcMatrix.outputTranslate', targetPMA + ".input3D[0]")
cmds.connectAttr('base_loc_dcMatrix.outputTranslate', targetPMA + ".input3D[1]")
cmds.connectAttr('const_loc_dcMatrix.outputTranslate', constPMA + ".input3D[0]")
cmds.connectAttr('base_loc_dcMatrix.outputTranslate', constPMA + ".input3D[1]")
cmds.connectAttr('pose_loc_dcMatrix.outputTranslate', posePMA + ".input3D[0]")
cmds.connectAttr('base_loc_dcMatrix.outputTranslate', posePMA + ".input3D[1]")
targetAng = cmds.shadingNode('angleBetween', n= 'target_angle', asUtility=1)
poseAng = cmds.shadingNode('angleBetween', n= 'pose_angle', asUtility=1)
cmds.connectAttr(targetPMA + '.output3D', targetAng + '.vector1')
cmds.connectAttr(constPMA + '.output3D', targetAng + '.vector2')
cmds.connectAttr(targetPMA + '.output3D', poseAng + '.vector1')
cmds.connectAttr(posePMA + '.output3D', poseAng + '.vector2')
#cmds.connectAttr('target_angle.angle','poseReader_grp.outputAngle')

#Divide Target by Pose
poseMD = cmds.shadingNode('multiplyDivide', n = 'pose_MD', asUtility=1)
cmds.setAttr(poseMD + '.operation',2)
cmds.connectAttr(targetAng + '.angle', poseMD + '.input1X')
cmds.connectAttr(poseAng + '.angle', poseMD + '.input2X')
poseClamp = cmds.shadingNode('clamp',n="pose_clamp", asUtility=1)
cmds.setAttr(poseClamp + '.maxR',1)
cmds.connectAttr(poseMD + '.outputX',poseClamp + '.inputR')
shiftDownPMA = cmds.shadingNode('plusMinusAverage', n='shiftDown_PMA', asUtility=1)
reverseNormalized = cmds.shadingNode('multiplyDivide', n='reverseOutput', asUtility=1)
cmds.setAttr(shiftDownPMA + '.operation',2)
cmds.setAttr(shiftDownPMA + '.input1D[1]',1)
cmds.setAttr(reverseNormalized + '.input2X',-1)
cmds.connectAttr(poseClamp + '.outputR', shiftDownPMA + '.input1D[0]')
cmds.connectAttr(shiftDownPMA + '.output1D', reverseNormalized + '.input1X')
cmds.connectAttr(reverseNormalized + '.outputX', grp + '.outputAngle')

#Constaint to Selection
if len(constSel) == 2:
    cmds.pointConstraint(constSel[1],grp)
    aimToGo = cmds.aimConstraint(constSel[0],grp,aim=(1,0,0),u=(0,1,0))
    cmds.delete(aimToGo)
else:
    cmds.error("Select the target then select and base and run this script again.")
    
