import maya.cmds as cmds

#Declare Selection for constraints
constSel = cmds.ls(sl=1)
lineNo = 8

def createPR():
    #Create Locators and set position and override colours 
    baseLoc = cmds.spaceLocator(n = "base_loc")[0]
    targetLoc = cmds.spaceLocator(n = "target_loc")[0]
    constLoc = cmds.spaceLocator(n = "const_loc")[0]
    poseLoc = cmds.spaceLocator(n = "pose_loc")[0]
    cmds.xform(targetLoc,t=(0,1,0))
    cmds.xform(constLoc,t=(1,1,0))
    cmds.xform(poseLoc,t=(1,1,0))
    poseRLoc = [baseLoc,targetLoc,constLoc]
    for prl in poseRLoc:
        cmds.setAttr(prl+"Shape.overrideEnabled", 1)
        cmds.setAttr(prl+"Shape.overrideColor", 17)
    
    #Create Coneshape and set xfrom
        #lines
    lineShapes = []
    for i in range (0,lineNo):
        lineR = (360 / lineNo)*i
        line = cmds.curve(d = 1, p =[(0,0,0),(0,1,-1)],k = [0, 1], n = "coneLine" + str(i))
        xRot = cmds.getAttr(line + '.rotateY') + lineR
        cmds.setAttr(line + '.rotateY',xRot)
        cmds.setAttr((cmds.listRelatives(line, type = 'shape')[0] + ".overrideEnabled"),1)
        cmds.setAttr((cmds.listRelatives(line, type = 'shape')[0] + ".overrideColor"),18)
        cmds.makeIdentity(line,a=1,r=1)
        lineShapes.append(line)
        
        #circle
    csc1 = cmds.circle(c= (0,1,0),nr = (0,1,0), sw = 360, r = 1, s = 8,ch = 0)
    cmds.setAttr((cmds.listRelatives(csc1, type = 'shape')[0] + ".overrideEnabled"),1)
    cmds.setAttr((cmds.listRelatives(csc1, type = 'shape')[0] + ".overrideColor"),18)
        #put em together
    for lShp in lineShapes:
        cmds.parent((cmds.listRelatives(lShp, type = 'shape')),csc1,s=1,r=1)
        cmds.delete(lShp)
    cmds.rename(csc1,"cone_01")
    
    #Create Cone Adjustment Handle
    coneAdj = cmds.curve(d=1, p=[(-1,0,1),(1,0,1),(1,0,-1),(-1,0,-1),(-1,0,1)], k=[0,1,2,3,4], n= "cone_CTRL")
    cmds.setAttr((cmds.listRelatives(coneAdj, type="shape")[0] +".overrideEnabled"),1)
    cmds.setAttr((cmds.listRelatives(coneAdj, type="shape")[0] +".overrideColor"),14)
    cmds.xform(coneAdj,ro=(90,0,0),s=(0.333,0.333,0.333),t = (0,0,0))
    cmds.makeIdentity(coneAdj,a=1, r=1, s=1, t=1)
    cmds.connectAttr(coneAdj + '.translateX',poseLoc + '.translateX')
    cmds.connectAttr(coneAdj + '.translateY',poseLoc + '.translateY')
    cmds.setAttr(poseLoc + '.visibility',0)
    
    #Connect Cone Adjustment Translate to Scale of Cone Shape
    cmds.connectAttr(coneAdj + '.translateX', 'cone_01.scaleX')
    cmds.connectAttr(coneAdj + '.translateY', 'cone_01.scaleY')
    cmds.connectAttr(coneAdj + '.translateY', 'cone_01.scaleZ')

    #Group all viewable thingies
    grp = cmds.group("cone_01",coneAdj,baseLoc,targetLoc,constLoc,poseLoc,n="poseReader_grp")
    cmds.move(0,0,0,grp + '.scalePivot', grp + '.rotatePivot')
    cmds.setAttr(grp + '.rotateZ', -90)
    cmds.makeIdentity(grp,a=1,r=1)
    cmds.setAttr(coneAdj + '.translateZ',l=1,k=0,cb=0)
    cmds.setAttr(coneAdj + '.rotateX',l=1,k=0,cb=0)
    cmds.setAttr(coneAdj + '.rotateY',l=1,k=0,cb=0)
    cmds.setAttr(coneAdj + '.rotateZ',l=1,k=0,cb=0)
    cmds.setAttr(coneAdj + '.scaleX',l=1,k=0,cb=0)
    cmds.setAttr(coneAdj + '.scaleY',l=1,k=0,cb=0)
    cmds.setAttr(coneAdj + '.scaleZ',l=1,k=0,cb=0)
    cmds.addAttr(grp, ln = 'outputAngle', at="float", r=1, h=0, k=0)
    
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
    
    cmds.setAttr(coneAdj + '.translateX',1)
    cmds.setAttr(coneAdj + '.translateY',-1)
    
    #Constaint to Selection    
    cmds.pointConstraint(constSel[1],grp)
    aimToGo = cmds.aimConstraint(constSel[0],grp,aim=(1,0,0),u=(0,1,0))
    cmds.delete(aimToGo)

if len(constSel) == 2:
    createPR()
else:
    cmds.error("Select the target then select and base and run this script again.")
