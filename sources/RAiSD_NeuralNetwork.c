/*  
 *  RAiSD, Raised Accuracy in Sweep Detection
 *
 *  Copyright January 2017 by Nikolaos Alachiotis and Pavlos Pavlidis
 *
 *  This program is free software; you may redistribute it and/or modify its
 *  under the terms of the GNU General Public License as published by the Free
 *  Software Foundation; either version 2 of the License, or (at your option)
 *  any later version.
 *
 *  This program is distributed in the hope that it will be useful, but
 *  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
 *  or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
 *  for more details.
 *
 *  For any other enquiries send an email to
 *  Nikolaos Alachiotis (n.alachiotis@gmail.com)
 *  Pavlos Pavlidis (pavlidisp@gmail.com)  
 *  
 */
 
#ifdef _RSDAI

#include "RAiSD.h"

RSDNeuralNetwork_t * RSDNeuralNetwork_new (RSDCommandLine_t * RSDCommandLine)
{
	assert(RSDCommandLine!=NULL);
	
	if(RSDCommandLine->opCode!=OP_TRAIN_CNN && RSDCommandLine->opCode!=OP_TEST_CNN && RSDCommandLine->opCode!=OP_USE_CNN)
		return NULL;
		
	RSDNeuralNetwork_t * nn = (RSDNeuralNetwork_t *)malloc(sizeof(RSDNeuralNetwork_t));
	assert(nn!=NULL);
	
	strncpy(nn->pyPath, "\0", STRING_SIZE);
	strncpy(nn->cnnMode, "\0", STRING_SIZE);
	nn->imageHeight = 0;
	nn->imageWidth = 0;
	nn->dataFormat = 0; // default: images (PNG)
	nn->dataType = -1;
	strncpy(nn->networkArchitecture, "\0", STRING_SIZE);	
	nn->epochs = 0;
	strncpy(nn->inputPath, "\0", STRING_SIZE);
	strncpy(nn->modelPath, "\0", STRING_SIZE);
	strncpy(nn->outputPath, "\0", STRING_SIZE);
	nn->classSize = 0;
	nn->classLabel = NULL;
	strncpy(nn->cl4_1x_label, "cl4_1x_label", STRING_SIZE);
	strncpy(nn->cl4_x1_label, "cl4_x1_label", STRING_SIZE); 	
	
	return nn;
}

void read_img_nn_info_file (char * path, int mode, FILE * fpOut, int * width, int * height, char * format, char * architecture, int * dataType, int * enTF, int * en2x2, int * groups)
{
	assert(path!=NULL);
	assert(mode==0 || mode==1);
	assert(fpOut!=NULL);
	assert(width!=NULL);
	assert(height!=NULL);
	assert(format!=NULL);
	
	char tstring[STRING_SIZE];
	
	FILE * fp = fopen(path, "r");
	
	if(fp==NULL)
	{
		if(mode==0)
		{
			fprintf(fpOut, "\nERROR: File %s with input image dimensions not found!\n\n", path);		
			fprintf(stderr, "\nERROR: File %s with input image dimensions not found!\n\n", path);
		}
		else
		{
			fprintf(fpOut, "\nERROR: File %s with expected input image dimensions not found!\n\n", path);		
			fprintf(stderr, "\nERROR: File %s with expected input image dimensions not found!\n\n", path);			
		}
		
		exit(1);
	}
	else
	{		
		int ret = fscanf(fp, "%s %d %d %s %d", tstring, width, height, format, dataType);
		assert(ret==5);
		
		if(mode==1)
		{
			assert(architecture!=NULL);
			ret = fscanf(fp, "%s", architecture);
			assert(ret==1);
			
			assert(enTF!=NULL);
			ret = fscanf(fp, "%d", enTF);
			assert(ret==1);
			
			assert(en2x2!=NULL);
			ret = fscanf(fp, "%d", en2x2);
			assert(ret==1);
			
			assert(groups!=NULL);
			ret = fscanf(fp, "%d", groups);
			assert(ret==1);	
		}
		fclose(fp);
	}
	
	assert(*width>=3);
	assert(*height>=3);
	assert(!strcmp(format, "bin") || !strcmp(format, "2D"));		
}

void RSDNeuralNetwork_init (RSDNeuralNetwork_t * RSDNeuralNetwork, RSDCommandLine_t * RSDCommandLine, FILE * fpOut)
{
	if(RSDNeuralNetwork==NULL)
		return;
		
	assert(RSDCommandLine!=NULL);
	
	char tstring[STRING_SIZE];

	FILE * fp = NULL;
	int i=-1, ret=-1;
	
	switch(RSDCommandLine->opCode)
	{
		case OP_TRAIN_CNN:
			strncpy(RSDNeuralNetwork->inputPath, RSDCommandLine->inputFileName, STRING_SIZE);
			
			strncpy(RSDNeuralNetwork->modelPath, "RAiSD_Model.", STRING_SIZE); 
			strcat(RSDNeuralNetwork->modelPath, RSDCommandLine->runName);
			
			strncpy(RSDNeuralNetwork->outputPath, "RAiSD_Model.", STRING_SIZE); 
			strcat(RSDNeuralNetwork->outputPath, RSDCommandLine->runName);
			
			RSDNeuralNetwork->classSize = numOfClasses_NN_architecture (RSDCommandLine->networkArchitecture, RSDCommandLine->classification2x2En);
			
			RSDNeuralNetwork->classLabel = (char**)rsd_malloc(sizeof(char*)*RSDNeuralNetwork->classSize);
			assert(RSDNeuralNetwork->classLabel!=NULL);
			
			for(i=0;i<RSDNeuralNetwork->classSize;i++)
			{
				RSDNeuralNetwork->classLabel[i]=(char*)rsd_malloc(sizeof(char)*STRING_SIZE);
				assert(RSDNeuralNetwork->classLabel[i]!=NULL);				
			}
				
			strncpy(RSDNeuralNetwork->cl4_1x_label, RSDCommandLine->cl4_1x_label, STRING_SIZE);
			strncpy(RSDNeuralNetwork->cl4_x1_label, RSDCommandLine->cl4_x1_label, STRING_SIZE);			
		break;
		
		case OP_TEST_CNN:
			strncpy(RSDNeuralNetwork->inputPath, "RAiSD_Images.", STRING_SIZE);
			strcat(RSDNeuralNetwork->inputPath, RSDCommandLine->runName);
			
			strcpy(RSDNeuralNetwork->modelPath, RSDCommandLine->modelPath);
			
			strncpy(tstring, RSDNeuralNetwork->modelPath, STRING_SIZE);  
			strcat(tstring, "/classLabels.txt");
			
			fp = fopen(tstring, "r");
			if(fp==NULL)
			{
				fprintf(fpOut, "\nERROR: File %s with class labels not found!\n\n",tstring);		
				fprintf(stderr, "\nERROR: File %s with class labels not found!\n\n",tstring);
				
				exit(1);
			}
			
			ret = fscanf(fp, "%s %d", tstring, &RSDNeuralNetwork->classSize);
			assert(ret==2);
			
			RSDNeuralNetwork->classLabel = (char**)rsd_malloc(sizeof(char*)*RSDNeuralNetwork->classSize);
			assert(RSDNeuralNetwork->classLabel!=NULL);
			
			for(i=0;i<RSDNeuralNetwork->classSize;i++)
			{
				RSDNeuralNetwork->classLabel[i]=(char*)rsd_malloc(sizeof(char)*STRING_SIZE);
				assert(RSDNeuralNetwork->classLabel[i]!=NULL);
				
				ret = fscanf(fp, "%s %s", RSDNeuralNetwork->classLabel[i], tstring);
				assert(ret==2);
			}	
			
			fclose(fp);
			
			strncpy(RSDNeuralNetwork->outputPath, "RAiSD_Model.", STRING_SIZE); 
			strcat(RSDNeuralNetwork->outputPath, RSDCommandLine->runName);
		break;
		
		case OP_USE_CNN:
			
			strcpy(RSDNeuralNetwork->modelPath, RSDCommandLine->modelPath);
			
			strncpy(tstring, RSDNeuralNetwork->modelPath, STRING_SIZE);  
			strcat(tstring, "/classLabels.txt");
			
			fp = fopen(tstring, "r");
			if(fp==NULL)
			{
				fprintf(fpOut, "\nERROR: File %s with class labels not found!\n\n",tstring);		
				fprintf(stderr, "\nERROR: File %s with class labels not found!\n\n",tstring);
				
				exit(1);
			}
			
			ret = fscanf(fp, "%s %d", tstring, &RSDNeuralNetwork->classSize);
			assert(ret==2);
				
			RSDNeuralNetwork->classLabel = (char**)rsd_malloc(sizeof(char*)*RSDNeuralNetwork->classSize);
			assert(RSDNeuralNetwork->classLabel!=NULL);
			
			for(i=0;i<RSDNeuralNetwork->classSize;i++)
			{
				RSDNeuralNetwork->classLabel[i]=(char*)rsd_malloc(sizeof(char)*STRING_SIZE);
				assert(RSDNeuralNetwork->classLabel[i]!=NULL);
				
				ret = fscanf(fp, "%s %s", RSDNeuralNetwork->classLabel[i], tstring);
				assert(ret==2);
			}
			
			if(RSDNeuralNetwork->classSize==4) // only FASTER-NN-G-2x2
			{
				ret = fscanf(fp, "%s", RSDNeuralNetwork->cl4_1x_label);
				assert(ret==1);	
			
				ret = fscanf(fp, "%s", RSDNeuralNetwork->cl4_x1_label);
				assert(ret==1);	
			}
			
			fclose(fp);			
		break;
	
		default:
			assert(0);
	
	}
	
	/* Dimension checks */
	/* Training: read image dims from -I input file, set network dims */
	/* Testing: read image dims from -I input file, read network dims, check match */
	/* Using: read network dims only */	
	
	int imgHeight=-1, imgWidth=-1, imgDataType=-1, enTF=0;
	char imgFormat[STRING_SIZE], imgFormat2[STRING_SIZE];
	
	if(RSDCommandLine->opCode==OP_TRAIN_CNN || RSDCommandLine->opCode==OP_TEST_CNN)
	{
		// Load input image dimensions and format			
		strncpy(tstring, RSDCommandLine->inputFileName, STRING_SIZE);
		strcat(tstring, "/info.txt");
		
		read_img_nn_info_file (tstring, 0, fpOut, &imgWidth, &imgHeight, imgFormat, NULL, &imgDataType, NULL, NULL, NULL);
	}
	
	if(RSDCommandLine->opCode==OP_TEST_CNN || RSDCommandLine->opCode==OP_USE_CNN)
	{
		// Load expected input image dimensions and format
		strncpy(tstring, RSDNeuralNetwork->modelPath, STRING_SIZE);
		strcat(tstring, "/info.txt");
		
		read_img_nn_info_file (tstring, 1, fpOut, &RSDNeuralNetwork->imageWidth, &RSDNeuralNetwork->imageHeight, imgFormat2, RSDNeuralNetwork->networkArchitecture, 
				       &RSDNeuralNetwork->dataType, &enTF, &RSDCommandLine->classification2x2En, &RSDCommandLine->fasterNNgroups);
				       
		RSDNeuralNetwork->dataFormat = !strcmp(imgFormat2, "bin")?1:0;
		assert(enTF==0 || enTF==1);		
	}
				
	switch(RSDCommandLine->opCode)
	{
		case OP_TRAIN_CNN: 
			RSDNeuralNetwork->imageHeight = imgHeight;
			RSDNeuralNetwork->imageWidth = imgWidth;
			RSDNeuralNetwork->dataFormat = !strcmp(imgFormat, "bin")?1:0;
			strcpy(RSDNeuralNetwork->networkArchitecture, RSDCommandLine->networkArchitecture); 
			RSDNeuralNetwork->dataType = imgDataType;
			
			if(RSDCommandLine->enTF==1 && RSDNeuralNetwork->dataFormat==1)
			{
				fprintf(fpOut, "\nERROR: The TensorFlow implementation does not currently support binary input. You can use the PyTorch implementation instead.\n\n");
				fprintf(stderr, "\nERROR: The TensorFlow implementation does not currently support binary input. You can use the PyTorch implementation instead.\n\n");
				exit(1);
			}
			
			if(!strcmp(RSDNeuralNetwork->networkArchitecture, ARC_FASTER_NN_G) && (RSDNeuralNetwork->dataFormat==1 && RSDNeuralNetwork->dataType==1))
			{
				fprintf(fpOut, "\nERROR: %s can only be used with raw image data.\n\n", RSDNeuralNetwork->networkArchitecture);
				fprintf(stderr, "\nERROR: %s can only be used with raw image data.\n\n", RSDNeuralNetwork->networkArchitecture);
				exit(1);			
			}
			
						
		break;
		
		case OP_TEST_CNN:
			if(strcmp(imgFormat, imgFormat2))
			{
				fprintf(fpOut, "\nERROR: Input image format (%s) is incompatible with the trained model (expected %s)!\n\n",!strcmp(imgFormat, "bin")?"binary":"PNG", 
																	    !strcmp(imgFormat2, "bin")?"binary":"PNG");		
				fprintf(stderr, "\nERROR: Input image format (%s) is incompatible with the trained model (expected %s)!\n\n", !strcmp(imgFormat, "bin")?"binary":"PNG", 
																	      !strcmp(imgFormat2, "bin")?"binary":"PNG");				
				exit(1);
			}
			
			if(imgWidth!=RSDNeuralNetwork->imageWidth)
			{
				fprintf(fpOut, "\nERROR: Input image width (%d) is incompatible with the trained model (expected %d)!\n\n", imgWidth, RSDNeuralNetwork->imageWidth);		
				fprintf(stderr, "\nERROR: Input image width (%d) is incompatible with the trained model (expected %d)!\n\n", imgWidth, RSDNeuralNetwork->imageWidth);
				
				exit(1);
			}
			
			if(imgHeight!=RSDNeuralNetwork->imageHeight)
			{
				if(!(strcmp(imgFormat, "bin")) && RSDNeuralNetwork->dataType==1)
				{
					fprintf(fpOut, "\nWARNING: Height mismatch between input images (%d) and the trained model (%d)! Classification accuracy might be negatively affected!\n\n", imgHeight, RSDNeuralNetwork->imageHeight);		
					fprintf(stderr, "\nWARNING: Height mismatch between input images (%d) and the trained model (%d)! Classification accuracy might be negatively affected!\n\n", imgHeight, RSDNeuralNetwork->imageHeight);
				}
				else
				{
					fprintf(fpOut, "\nERROR: Input image height (%d) is incompatible with the trained model (expected %d)!\n\n",imgHeight, RSDNeuralNetwork->imageHeight);		
					fprintf(stderr, "\nERROR: Input image height (%d) is incompatible with the trained model (expected %d)!\n\n", imgHeight, RSDNeuralNetwork->imageHeight);				
					
					exit(1);
				}
			}
				
			if(imgDataType!=RSDNeuralNetwork->dataType)
			{
				fprintf(fpOut, "\nERROR: Input image data-type code (%d) is incompatible with the trained model (expected %d)!\n\n",imgDataType, RSDNeuralNetwork->dataType);		
				fprintf(stderr, "\nERROR: Input image data-type code (%d) is incompatible with the trained model (expected %d)!\n\n", imgDataType, RSDNeuralNetwork->dataType);				
				
				exit(1);
			}
			
			if(enTF!=RSDCommandLine->enTF && RSDCommandLine->enTF==1)
			{
				fprintf(fpOut, "\nERROR: Model %s is implemented in PyTorch. Remove \"-useTF\".\n\n", RSDNeuralNetwork->modelPath);		
				fprintf(stderr, "\nERROR: Model %s is implemented in PyTorch. Remove \"-useTF\".\n\n", RSDNeuralNetwork->modelPath);			
				
				exit(1);
			}
			
			RSDCommandLine->enTF = enTF;
			
			if(RSDCommandLine->enTF==1 && RSDNeuralNetwork->dataFormat==1)
			{
				fprintf(fpOut, "\nERROR: The TensorFlow implementation does not currently support binary input. You can use the PyTorch implementation instead.\n\n");
				fprintf(stderr, "\nERROR: The TensorFlow implementation does not currently support binary input. You can use the PyTorch implementation instead.\n\n");
				exit(1);
			}
			
			strcpy(RSDCommandLine->networkArchitecture, RSDNeuralNetwork->networkArchitecture); 
		break;
		
		case OP_USE_CNN:
			imgHeight = RSDNeuralNetwork->imageHeight;
			imgWidth = RSDNeuralNetwork->imageWidth;
			strcpy(imgFormat, imgFormat2);
			imgDataType = RSDNeuralNetwork->dataType;
			
			// only width check here, the height check takes place when the sample size is known
			if(imgWidth!=RSDCommandLine->windowSize)
			{
				if(RSDCommandLine->userWindowSize==1)
				{
					fprintf(fpOut, "\nERROR: Sliding-window size (%d) is incompatible with the trained model (expected %d)!\n\n",(int)RSDCommandLine->windowSize, RSDNeuralNetwork->imageWidth);		
					fprintf(stderr, "\nERROR: Sliding-window size (%d) is incompatible with the trained model (expected %d)!\n\n",(int)RSDCommandLine->windowSize, RSDNeuralNetwork->imageWidth);
					fclose(fpOut);					
					exit(1);
				}
				else
					RSDCommandLine->windowSize = RSDNeuralNetwork->imageWidth;

			}
	
			RSDCommandLine->enBinFormat = RSDNeuralNetwork->dataFormat;
			RSDCommandLine->imgDataType = RSDNeuralNetwork->dataType;
			strcpy(RSDCommandLine->networkArchitecture, RSDNeuralNetwork->networkArchitecture); 
			
			if(numOfPositiveClasses_NN_architecture (RSDNeuralNetwork->networkArchitecture, RSDCommandLine->classification2x2En)!=RSDCommandLine->numOfPositiveClasses)
			{
				fprintf(fpOut, "\nERROR: The number of positive-class indices provided through -pci is incompatible with the trained model (expected %d).\n\n", numOfPositiveClasses_NN_architecture (RSDNeuralNetwork->networkArchitecture, RSDCommandLine->classification2x2En));		
				fprintf(stderr, "\nERROR: The number of positive-class indices provided through -pci is incompatible with the trained model (expected %d).\n\n", numOfPositiveClasses_NN_architecture (RSDNeuralNetwork->networkArchitecture, RSDCommandLine->classification2x2En));				
				
				exit(1);			
			}			
			
			for(i=0;i<RSDCommandLine->numOfPositiveClasses;i++)
			{
				if((RSDCommandLine->positiveClassIndex[i]<0) || (RSDCommandLine->positiveClassIndex[i]>=numOfClasses_NN_architecture (RSDNeuralNetwork->networkArchitecture, RSDCommandLine->classification2x2En)))
				{
					fprintf(fpOut, "\nERROR: Invalid positive-class index given through -pci (%d). Valid values: [0-%d].\n\n", RSDCommandLine->positiveClassIndex[i], numOfClasses_NN_architecture (RSDNeuralNetwork->networkArchitecture, RSDCommandLine->classification2x2En)-1);		
					fprintf(stderr, "\nERROR: Invalid positive-class index given through -pci (%d). Valid values: [0-%d].\n\n", RSDCommandLine->positiveClassIndex[i], numOfClasses_NN_architecture (RSDNeuralNetwork->networkArchitecture, RSDCommandLine->classification2x2En)-1);		
				
					exit(1);				
				}
			
			}	    		
			
			if(enTF!=RSDCommandLine->enTF && RSDCommandLine->enTF==1)
			{
				fprintf(fpOut, "\nERROR: Model %s is implemented in PyTorch. Remove \"-useTF\".\n\n", RSDNeuralNetwork->modelPath);		
				fprintf(stderr, "\nERROR: Model %s is implemented in PyTorch. Remove \"-useTF\".\n\n", RSDNeuralNetwork->modelPath);			
				
				exit(1);
			}
			
			RSDCommandLine->enTF = enTF;
			
			if(RSDCommandLine->enTF==1 && RSDNeuralNetwork->dataFormat==1)
			{
				fprintf(fpOut, "\nERROR: The TensorFlow implementation does not currently support binary input. You can use the PyTorch implementation instead.\n\n");
				fprintf(stderr, "\nERROR: The TensorFlow implementation does not currently support binary input. You can use the PyTorch implementation instead.\n\n");
				
				exit(1);
			}			
		break;
	
		default:
			assert(0);	
	}
	
	RSDNeuralNetwork_printDependencies (RSDCommandLine, RAiSD_Info_FP);
	
	assert(imgWidth==RSDNeuralNetwork->imageWidth);

	if(!(!(strcmp(imgFormat, "bin")) && RSDNeuralNetwork->dataType==1))
		assert(imgHeight==RSDNeuralNetwork->imageHeight);

	assert((!strcmp(imgFormat, "bin")?1:0)==RSDNeuralNetwork->dataFormat);
	
	fprintf(fpOut, " Image width\t     :\t%d (window width)\n", imgWidth);
	fprintf(stdout, " Image width\t     :\t%d (window width)\n", imgWidth);
			
	fprintf(fpOut, " Image height\t     :\t%d (sample size)\n", imgHeight);
	fprintf(stdout, " Image height\t     :\t%d (sample size)\n", imgHeight);
	
	fprintf(fpOut, " File format\t     :\t%s\n", !strcmp(imgFormat, "bin")?"binary":"PNG");
	fprintf(stdout, " File format\t     :\t%s\n", !strcmp(imgFormat, "bin")?"binary":"PNG");
	
	fprintf(fpOut, " Data type\t     :\t%s\n", getDataType_string (imgFormat, imgDataType));
	fprintf(stdout, " Data type\t     :\t%s\n", getDataType_string (imgFormat, imgDataType));
	
	if(!strcmp(imgFormat, "bin") && imgDataType==BIN_DATA_ALLELE_COUNT && RSDCommandLine->classification2x2En==1 && !strcmp(RSDCommandLine->networkArchitecture, ARC_SWEEPNETRECOMB))
	{
		fprintf(fpOut, "\nERROR: Network architecture SweepNetRecombination does not support allele frequencies as input!\n\n");		
		fprintf(stderr, "\nERROR: Network architecture SweepNetRecombination does not support allele frequencies as input!\n\n");
		
		exit(1);
	}	 
	
	//Python source files path and check
	strncpy(RSDNeuralNetwork->pyPath, _COMPILE_PATH, STRING_SIZE);
	if(RSDCommandLine->enTF==1)
		strncat(RSDNeuralNetwork->pyPath, "/sources/tensorflow-sources/NN.py", STRING_SIZE);
	else
		strncat(RSDNeuralNetwork->pyPath, "/sources/pytorch-sources/main.py", STRING_SIZE);
		
	fp = fopen(RSDNeuralNetwork->pyPath, "r");
	if(fp==NULL)
	{
		fprintf(fpOut, "\n\nERROR: Python source files not found at %s/sources/pytorch-sources\n", _COMPILE_PATH);
		fprintf(stderr, "\n\nERROR: Python source files not found at %s/sources/pytorch-sources\n", _COMPILE_PATH);
	
		exit(1);
	}
	assert(fp!=NULL);
	fclose(fp);	
	
	char 	filenameClassNumErr[STRING_SIZE/4], 
		filenameClassNumErr2[STRING_SIZE/4], 
		filenameClassNumCnt[STRING_SIZE/4], 
		filenameClassLbl[STRING_SIZE/4], 
		command[STRING_SIZE*2], 
		runNameSanitized [STRING_SIZE/8];

	sanitizeString(RSDCommandLine->runName, runNameSanitized, STRING_SIZE/8);
	
	snprintf(filenameClassNumErr, STRING_SIZE/4, "%s-%s-%s", "checkClassNumErr", runNameSanitized, "rsdai.txt");
	snprintf(filenameClassNumErr2, STRING_SIZE/4, "%s-%s-%s", "checkClassNumErr2", runNameSanitized, "rsdai.txt");
	snprintf(filenameClassNumCnt, STRING_SIZE/4, "%s-%s-%s", "checkClassNumCnt", runNameSanitized, "rsdai.txt");
	snprintf(filenameClassLbl, STRING_SIZE/4, "%s-%s-%s", "checkClassLbl", runNameSanitized, "rsdai.txt");	 	
	
	if(RSDCommandLine->opCode==OP_TRAIN_CNN || RSDCommandLine->opCode==OP_TEST_CNN)
	{	
		snprintf(command, STRING_SIZE, "rm %s 1>>/dev/null 2>>/dev/null", filenameClassNumErr);
		exec_command(command);

		snprintf(command, STRING_SIZE, "rm %s 1>>/dev/null 2>>/dev/null", filenameClassNumErr2);
		exec_command(command);

		snprintf(command, STRING_SIZE, "rm %s 1>>/dev/null 2>>/dev/null", filenameClassNumCnt);
		exec_command(command);
		
		snprintf(command, STRING_SIZE, "rm %s 1>>/dev/null 2>>/dev/null", filenameClassLbl);
		exec_command(command);		
		
		snprintf(command, STRING_SIZE*2, "find %s -mindepth 1 -maxdepth 1 -type d 1> %s 2>>%s", RSDCommandLine->inputFileName, filenameClassLbl, filenameClassNumErr);
		exec_command(command);	
		
		snprintf(command, STRING_SIZE*2, "find %s -mindepth 1 -maxdepth 1 -type d 2>>%s | wc -l 1>%s 2>>%s", RSDCommandLine->inputFileName, filenameClassNumErr, filenameClassNumCnt, filenameClassNumErr2);
		exec_command(command);		
		
		fp = fopen(filenameClassNumErr, "r");
		assert(fp!=NULL);
		
		ret=fscanf(fp, "%s", tstring);
		//assert(ret==1);
		
		if(!strcmp(tstring, "find:"))
		{
			fprintf(fpOut, "\nERROR: Directory %s not found!\n\n",RSDCommandLine->inputFileName);		
			fprintf(stderr, "\nERROR: Directory %s not found!\n\n",RSDCommandLine->inputFileName);
			
			snprintf(command, STRING_SIZE, "rm %s 1>>/dev/null 2>>/dev/null", filenameClassNumErr);
			exec_command(command);

			snprintf(command, STRING_SIZE, "rm %s 1>>/dev/null 2>>/dev/null", filenameClassNumErr2);
			exec_command(command);

			snprintf(command, STRING_SIZE, "rm %s 1>>/dev/null 2>>/dev/null", filenameClassNumCnt);
			exec_command(command);
			
			snprintf(command, STRING_SIZE, "rm %s 1>>/dev/null 2>>/dev/null", filenameClassLbl);
			exec_command(command);		

			fclose(fp);			
			exit(1);
		}
		else
		{
			fclose(fp);
			
			fp = fopen(filenameClassNumCnt, "r");
			assert(fp!=NULL);
			
			int classes=-1;
			
			ret=fscanf(fp, "%d", &classes);
			assert(ret==1);
				
			if(classes!=numOfClasses_NN_architecture(RSDCommandLine->networkArchitecture, RSDCommandLine->classification2x2En))
			{
				fprintf(fpOut, "\nERROR: %d class folder(s) found in directory %s (%s requires %d)!\n\n", classes, 
														RSDCommandLine->inputFileName,
														RSDCommandLine->networkArchitecture,
														numOfClasses_NN_architecture(RSDCommandLine->networkArchitecture, RSDCommandLine->classification2x2En));
																
				fprintf(stderr, "\nERROR: %d class folder(s) found in directory %s (%s requires %d)!\n\n", classes, 
														RSDCommandLine->inputFileName,
														RSDCommandLine->networkArchitecture,
														numOfClasses_NN_architecture(RSDCommandLine->networkArchitecture, RSDCommandLine->classification2x2En));
				
				snprintf(command, STRING_SIZE, "rm %s 1>>/dev/null 2>>/dev/null", filenameClassNumErr);
				exec_command(command);

				snprintf(command, STRING_SIZE, "rm %s 1>>/dev/null 2>>/dev/null", filenameClassNumErr2);
				exec_command(command);

				snprintf(command, STRING_SIZE, "rm %s 1>>/dev/null 2>>/dev/null", filenameClassNumCnt);
				exec_command(command);
				
				snprintf(command, STRING_SIZE, "rm %s 1>>/dev/null 2>>/dev/null", filenameClassLbl);
				exec_command(command);
				
				fclose(fp);			
				exit(1);
			}
			else
			{
				fclose(fp);
				
				if(RSDCommandLine->opCode==OP_TRAIN_CNN)
				{				
					fp = fopen(filenameClassLbl, "r");
					assert(fp!=NULL);
					
					int i=-1;
					for(i=0;i<classes;i++)
					{
						int ret = fscanf(fp, "%s", tstring);
						assert(ret==1);
						
						int j=-1;
						for(j=strlen(tstring)-1;j>=0 && tstring[j]!='/';j--);
						
						assert(tstring[j]=='/');
						
						strcpy(RSDNeuralNetwork->classLabel[i], tstring+j+1);
					}
					
					fclose(fp);
				}
					
				snprintf(command, STRING_SIZE, "rm %s 1>>/dev/null 2>>/dev/null", filenameClassNumErr);
				exec_command(command);

				snprintf(command, STRING_SIZE, "rm %s 1>>/dev/null 2>>/dev/null", filenameClassNumErr2);
				exec_command(command);

				snprintf(command, STRING_SIZE, "rm %s 1>>/dev/null 2>>/dev/null", filenameClassNumCnt);
				exec_command(command);
				
				snprintf(command, STRING_SIZE, "rm %s 1>>/dev/null 2>>/dev/null", filenameClassLbl);
				exec_command(command);			
			}
		}
	}
}

void RSDNeuralNetwork_free (RSDNeuralNetwork_t * RSDNeuralNetwork)
{
	if(RSDNeuralNetwork==NULL)
		return;
		
	if(RSDNeuralNetwork->classLabel!=NULL)
	{
		for(int i=0;i<RSDNeuralNetwork->classSize;i++)
			if(RSDNeuralNetwork->classLabel[i]!=NULL)
				free(RSDNeuralNetwork->classLabel[i]);
				
		free(RSDNeuralNetwork->classLabel);
	}	
	
	free(RSDNeuralNetwork);
	
	RSDNeuralNetwork=NULL;
}

int RSDNeuralNetwork_modelExists (char * modelPath)
{
	assert(modelPath!=NULL);
	
	char tstringTF[STRING_SIZE], tstringPT[STRING_SIZE];
	
	strcpy(tstringTF, modelPath);
	strcpy(tstringPT, modelPath);
	
	strcat(tstringTF, "/weights.best.hdf5");
	strcat(tstringPT, "/model.pt");
	
	FILE * fpTF = fopen(tstringTF, "r");
	FILE * fpPT = fopen(tstringPT, "r");
	
	if(fpTF==NULL && fpPT==NULL)
		return 0;
		
	if(fpTF!=NULL)
		fclose(fpTF);
		
	if(fpPT!=NULL)
		fclose(fpPT);
		
	return 1;
}

void RSDNeuralNetwork_createTrainCommand (RSDNeuralNetwork_t * RSDNeuralNetwork, RSDCommandLine_t * RSDCommandLine, char * trainCommand, int showErrors)
{
	assert(RSDNeuralNetwork!=NULL);
	assert(RSDCommandLine!=NULL);
	assert(trainCommand!=NULL);
	
	char tstring[STRING_SIZE];

	if(RSDCommandLine->forceRemove==1)
	{
		strncpy(tstring, "rm -r ", STRING_SIZE);
		strcat(tstring, RSDNeuralNetwork->modelPath);
		strcat(tstring, " 2>/dev/null");

		exec_command (tstring);	
	}
		
	strncpy(trainCommand, "python3 ", STRING_SIZE);
	strcat(trainCommand, RSDNeuralNetwork->pyPath);
	
	if(RSDCommandLine->enTF==1)
	{
		strcat(trainCommand, " -n ");
		strcat(trainCommand, "train");
	
		strcat(trainCommand, " -m ");
		strcat(trainCommand, RSDCommandLine->networkArchitecture);
	
		strcat(trainCommand, " -d ");
		strcat(trainCommand, RSDNeuralNetwork->inputPath);
	}
	else
	{
		strcat(trainCommand, " -a "); 
		strcat(trainCommand, "RAiSD_Info.");
		strcat(trainCommand, RSDCommandLine->runName);			
		
		strcat(trainCommand, " -m ");
		strcat(trainCommand, "train");
		
		strcat(trainCommand, " -r ");
		strcat(trainCommand, RSDNeuralNetwork->dataType==BIN_DATA_ALLELE_COUNT?"1":"0"); // 1: using the reduction (allele freq. + distances), 0: raw snp data and distances
	
		strcat(trainCommand, " -i ");
		strcat(trainCommand, RSDNeuralNetwork->inputPath);
		
		strcat(trainCommand, " -p ");
		if(RSDCommandLine->useGPU==1)
			strcat(trainCommand, "cuda");
		else
			strcat(trainCommand, "cpu"); 
		
		strcat(trainCommand, " -t ");
		sprintf(tstring, "%d", RSDCommandLine->threads);
		strcat(trainCommand, tstring);

		strcat(trainCommand, " -b ");
		strcat(trainCommand, "8"); // empirically determined, TODO from commandline?
		
		strcat(trainCommand, " -c ");
		strcat(trainCommand, RSDCommandLine->networkArchitecture); 
		
		assert(!strcmp(ARC_SWEEPNETRECOMB, ARC_FASTER_NN_G));
		
		if(!strcmp(RSDCommandLine->networkArchitecture, ARC_FASTER_NN_G))
		{	
			if(RSDCommandLine->fasterNNgroups==0)
			{
				RSDCommandLine->fasterNNgroups =  RSDNeuralNetwork->imageHeight;
			}
			else
			{
				RSDCommandLine->fasterNNgroups = getValidNumberOf_FASTER_NN_G_Groups (RSDNeuralNetwork->imageHeight, RSDCommandLine->fasterNNgroups);
			}
				
			strcat(trainCommand, " -g ");
			sprintf(tstring, "%d", RSDCommandLine->fasterNNgroups);
			strcat(trainCommand, tstring);			
		}
		
		if(RSDCommandLine->classification2x2En==1 && !strcmp(RSDCommandLine->networkArchitecture, ARC_SWEEPNETRECOMB))
		{
			int j=0;
			
			strcat(trainCommand, " -l ");
			strcat(trainCommand, "1");
			
			strcat(trainCommand, " -n ");				
			strcat(trainCommand, " \'[[\"");				
			strcat(trainCommand, RSDCommandLine->classPathList[j++]);
			strcat(trainCommand, "\",\"");
			strcat(trainCommand, RSDCommandLine->classPathList[j++]);
			strcat(trainCommand, "\"],[\"");
			strcat(trainCommand, RSDCommandLine->classPathList[j++]);
			strcat(trainCommand, "\",\"");
			strcat(trainCommand, RSDCommandLine->classPathList[j++]);
			strcat(trainCommand, "\"]]\'");
		}
		else
		{
			strcat(trainCommand, " -l ");
			strcat(trainCommand, "0");
		}
	
		strcat(trainCommand, " -f ");
		strcat(trainCommand, RSDNeuralNetwork->dataFormat==0?"0":"1"); // f=0 --> PNG, f=1 --> bin
		
		strcat(trainCommand, " -x ");
		strcat(trainCommand, RSDNeuralNetwork->dataFormat==1?"1":"0"); 
		
		strcat(trainCommand, " -y ");
		strcat(trainCommand, RSDCommandLine->trnObjDetection==0?"0":"1"); 	
	}
	
	strcat(trainCommand, " -h "); 
	sprintf(tstring, "%d", RSDNeuralNetwork->imageHeight);
	strcat(trainCommand, tstring);
	
	strcat(trainCommand, " -w "); 
	sprintf(tstring, "%d", RSDNeuralNetwork->imageWidth);
	strcat(trainCommand, tstring);

	strcat(trainCommand, " -e "); 
	sprintf(tstring, "%d", RSDCommandLine->epochs);
	strcat(trainCommand, tstring);
	
	strcat(trainCommand, " -o ");
	strcat(trainCommand, RSDNeuralNetwork->modelPath);
	
	if(showErrors==0)
		strcat(trainCommand, " 2>/dev/null");
	
	if((!RSDCommandLine->displayProgress)==1)
		strcat(trainCommand, " 1>/dev/null");	
		
}

void RSDNeuralNetwork_train (RSDNeuralNetwork_t * RSDNeuralNetwork, RSDCommandLine_t * RSDCommandLine, FILE * fpOut)
{
	if(RSDNeuralNetwork==NULL)
		return;
		
	if(RSDCommandLine->opCode!=OP_TRAIN_CNN)
		return;
		
	assert(RSDCommandLine!=NULL);
	assert(fpOut!=NULL);
	
	char trainCommand[STRING_SIZE], tstring[STRING_SIZE];

	RSDNeuralNetwork_createTrainCommand (RSDNeuralNetwork, RSDCommandLine, trainCommand, 0);		
		
	//fprintf(fpOut, " Training command    :\t%s\n", trainCommand);
	//fprintf(stdout, " Training command    :\t%s\n", trainCommand);
	
	
	if(!strcmp(RSDCommandLine->networkArchitecture, ARC_FASTER_NN_G))
	{
		fprintf(fpOut, "\n CNN training (%s, groups=%d) ...\n\n", RSDCommandLine->networkArchitecture, RSDCommandLine->fasterNNgroups);
		fprintf(stdout, "\n CNN training (%s, groups=%d) ...\n\n", RSDCommandLine->networkArchitecture, RSDCommandLine->fasterNNgroups);
	}
	else
	{
		fprintf(fpOut, "\n CNN training (%s) ...\n\n", RSDCommandLine->networkArchitecture);
		fprintf(stdout, "\n CNN training (%s) ...\n\n", RSDCommandLine->networkArchitecture);	
	}
	fflush(fpOut);
	fflush(stdout);
	
	fclose(fpOut);
	
	exec_command (trainCommand);
	
	strcpy(tstring, "RAiSD_Info.");
	strcat(tstring, RSDCommandLine->runName);	
	RAiSD_Info_FP = fopen(tstring, "a");
	
	fpOut = RAiSD_Info_FP;	
	
	strncpy(tstring, RSDNeuralNetwork->modelPath, STRING_SIZE);
	strcat(tstring, "/info.txt\0");
	
	FILE * fpImgDim = fopen(tstring, "w");
	assert(fpImgDim!=NULL);
	
	fprintf(fpImgDim, "***DO_NOT_REMOVE_OR_EDIT_THIS_FILE***\n");
	fprintf(fpImgDim, "%d\n%d\n", RSDNeuralNetwork->imageWidth, RSDNeuralNetwork->imageHeight);
	fprintf(fpImgDim, "%s\n%d\n%s\n", RSDNeuralNetwork->dataFormat==1?"bin":"2D", RSDNeuralNetwork->dataType, RSDNeuralNetwork->networkArchitecture);
	fprintf(fpImgDim, "%d\n", RSDCommandLine->enTF);
	fprintf(fpImgDim, "%d\n", RSDCommandLine->classification2x2En);
	fprintf(fpImgDim, "%d\n", RSDCommandLine->fasterNNgroups);
	fprintf(fpImgDim, "***DO_NOT_REMOVE_OR_EDIT_THIS_FILE***\n");
		
	fclose(fpImgDim);
	
	if(RSDCommandLine->classification2x2En==1 && !strcmp(RSDNeuralNetwork->networkArchitecture, ARC_SWEEPNETRECOMB))
	{
		strncpy(tstring, RSDNeuralNetwork->modelPath, STRING_SIZE);
		strcat(tstring, "/classLabels.txt\0");
		
		FILE * fpClasses = fopen(tstring, "w");
		assert(fpClasses!=NULL);
		
		fprintf(fpClasses, "***DO_NOT_REMOVE_OR_EDIT_THIS_FILE***\n");
		fprintf(fpClasses, "%d\n", RSDNeuralNetwork->classSize);	
		
		for(int i=0;i<RSDNeuralNetwork->classSize;i++)		
			fprintf(fpClasses, "%s (%d)\n", RSDCommandLine->classPathList[i], i);
			
		fprintf(fpClasses, "%s\n", RSDNeuralNetwork->cl4_1x_label);
		fprintf(fpClasses, "%s\n", RSDNeuralNetwork->cl4_x1_label);	
			
		fprintf(fpClasses, "***DO_NOT_REMOVE_OR_EDIT_THIS_FILE***\n");
		
		fclose(fpClasses);
	}
}

void RSDNeuralNetwork_modelCheck (RSDNeuralNetwork_t * RSDNeuralNetwork, RSDCommandLine_t * RSDCommandLine)
{
	assert(RSDNeuralNetwork!=NULL);
	assert(RSDCommandLine!=NULL);
	
	dir_exists_check (RSDNeuralNetwork->modelPath);
	
	char tstring[STRING_SIZE];		
	
	if(RSDCommandLine->enTF==1)
	{
		strncpy(tstring, RSDNeuralNetwork->modelPath, STRING_SIZE);
		strcat(tstring, "/weights.best.hdf5");
		FILE * fp = fopen(tstring, "r");
		if(fp==NULL)
		{
			fprintf(stderr, "\nERROR: File %s (Tensorflow) not found!\n\n", tstring);
			exit(1);
		}
		fclose(fp);
	}
	else
	{
		strncpy(tstring, RSDNeuralNetwork->modelPath, STRING_SIZE);
		strcat(tstring, "/model.pt");
		FILE * fp = fopen(tstring, "r");
		if(fp==NULL)
		{
			fprintf(stderr, "\nERROR: File %s (PyTorch) not found!\n\n", tstring);
			exit(1);
		}
		fclose(fp);
	}	
}

void RSDNeuralNetwork_createRunCommand (RSDNeuralNetwork_t * RSDNeuralNetwork, RSDCommandLine_t * RSDCommandLine, char * inputPath, char * runCommand)
{
	assert(RSDNeuralNetwork!=NULL);
	assert(RSDCommandLine!=NULL);
	assert(inputPath!=NULL);
	assert(runCommand!=NULL);
	
	RSDNeuralNetwork_modelCheck (RSDNeuralNetwork, RSDCommandLine);
	dir_exists_check (inputPath);
	
	char tstring[STRING_SIZE], runNameSanitized[STRING_SIZE/2], tstringF[STRING_SIZE];	
	
	strncpy(runCommand, "python3 ", STRING_SIZE);	
	strcat(runCommand, RSDNeuralNetwork->pyPath);
	
	if(RSDCommandLine->enTF==1)
	{
		strcat(runCommand, " -n ");
		strcat(runCommand, "predict");

		strcat(runCommand, " -m ");
		strcat(runCommand, RSDNeuralNetwork->modelPath);
		
		strcat(runCommand, " -d ");
		strcat(runCommand, inputPath);	
	}
	else
	{
		strcat(runCommand, " -m ");
		strcat(runCommand, "predict");
		
		strcat(runCommand, " -d ");
		strcat(runCommand, RSDNeuralNetwork->modelPath);		
		
		strcat(runCommand, " -i ");
		strcat(runCommand, inputPath);
		
		strcat(runCommand, " -p ");
		if(RSDCommandLine->useGPU==1)
			strcat(runCommand, "cuda");
		else
			strcat(runCommand, "cpu"); 
		
		strcat(runCommand, " -c ");
		strcat(runCommand, RSDNeuralNetwork->networkArchitecture); 

		strcat(runCommand, " -t ");
		sprintf(tstring, "%d", RSDCommandLine->threads);
		strcat(runCommand, tstring);
		
		strcat(runCommand, " -f ");
		strcat(runCommand, RSDNeuralNetwork->dataFormat==0?"0":"1"); // f=0 --> PNG, f=1 --> bin
		
		strcat(runCommand, " -x ");
		strcat(runCommand, RSDNeuralNetwork->dataFormat==1?"1":"0"); 
		
		strcat(runCommand, " -y ");
		strcat(runCommand, "0"); // training for detection, not used for inference, not implemented
		
		strcat(runCommand, " -r ");
		strcat(runCommand, RSDNeuralNetwork->dataType==BIN_DATA_ALLELE_COUNT?"1":"0"); // 1: using the reduction (allele freq. + distances), 0: raw snp data and distances
		
		strcat(runCommand, " -l ");
		strcat(runCommand, (RSDCommandLine->classification2x2En==1 && !strcmp(RSDCommandLine->networkArchitecture, ARC_SWEEPNETRECOMB))?"1":"0"); 
		
		if(!strcmp(RSDCommandLine->networkArchitecture, ARC_FASTER_NN_G))
		{
			strcat(runCommand, " -g ");
			sprintf(tstring, "%d", RSDCommandLine->fasterNNgroups);
			strcat(runCommand, tstring);
		}		
	}	
	
	strcat(runCommand, " -h ");
	sprintf(tstring, "%d", RSDNeuralNetwork->imageHeight);
	strcat(runCommand, tstring);
	
	strcat(runCommand, " -w ");
	sprintf(tstring, "%d", RSDNeuralNetwork->imageWidth);
	strcat(runCommand, tstring);	
	
	sanitizeString(RSDCommandLine->runName, runNameSanitized, STRING_SIZE/2);	
	snprintf(tstringF, STRING_SIZE, " -o tempOutputFolder-%s-rsdai", runNameSanitized);	
	strcat(runCommand, tstringF);

	strcat(runCommand, " 2>/dev/null");
	
	if(RSDCommandLine->dev)
	{
		printf("\nruncommand %s\n", runCommand);
		fflush(stdout);	
	}	
}

void RSDNeutralNetwork_run (RSDNeuralNetwork_t * RSDNeuralNetwork, RSDCommandLine_t * RSDCommandLine, void * RSDGrid, FILE * fpOut)
{
	assert(RSDNeuralNetwork!=NULL);
	assert(RSDCommandLine!=NULL);
	
	fprintf(stdout, "\n Predicting (using %s) ...\n", RSDNeuralNetwork->networkArchitecture);
	fprintf(fpOut, "\n Predicting (using %s) ...\n", RSDNeuralNetwork->networkArchitecture);
	
	if(RSDCommandLine->displayProgress==1)
	{
		fprintf(stdout, "\n");
		fprintf(fpOut, "\n");
	}
	
	char runCommand[STRING_SIZE];
	
	strncpy(runCommand, "rm ", STRING_SIZE); 
	strcat(runCommand, ((RSDGrid_t*)RSDGrid)->destinationPath);
	strcat(runCommand, "info.txt");  
	
	exec_command (runCommand);
	
	RSDNeuralNetwork_createRunCommand (RSDNeuralNetwork, RSDCommandLine, ((RSDGrid_t*)RSDGrid)->destinationPath, runCommand);	
	
	exec_command (runCommand);
}

int * RSDNeuralNetwork_readPredictionFile (RSDNeuralNetwork_t * RSDNeuralNetwork, FILE * fp, int classIndex, int numOfClasses, int * predictionGrid)
{
	assert(RSDNeuralNetwork!=NULL);
	assert(fp!=NULL);
	assert(classIndex>=0 && classIndex<=3);
	assert(numOfClasses>=2);
	assert(predictionGrid!=NULL);
	
	char tstring[STRING_SIZE];
	int i=0, ret=0, clIndex = -1;
	float p0=-1.0, p1=-1.0, p2=-1.0, p3=-1.0;
	
	assert(numOfClasses==2 || numOfClasses==4); // TODO: support any number of classes	
	
	int preds = numOfClasses/2;
	
	assert(preds==1 || preds==2);
	
	ret = fscanf(fp, "%s", tstring); // filename png or snp
	
	while(ret!=EOF)
	{
		// TODO: clean up prediction file and remove extra code from here
		for(i=0;i<preds;i++)
		{
			ret = fscanf(fp, "%d", &clIndex);
			assert(ret==1);
			assert(clIndex>=0);
		}
		
		ret = fscanf(fp, "%s", tstring);
		assert(ret==1);
		
		p0 = atof(tstring);
		
		ret = fscanf(fp, "%s", tstring);
		assert(ret==1);
		
		p1 = atof(tstring);
		
		assert(p0+p1<=1.0001f);			

		if(numOfClasses==4)
		{
			ret = fscanf(fp, "%s", tstring);
			assert(ret==1);
			
			p2 = atof(tstring);
			
			ret = fscanf(fp, "%s", tstring);
			assert(ret==1);
			
			p3 = atof(tstring);
			
			assert(p2+p3<=1.0001f);			
		}
		
		if(p0>=0.5)
			predictionGrid[classIndex*numOfClasses+0]++;
		else
			predictionGrid[classIndex*numOfClasses+1]++;
			
		if(numOfClasses==4)
		{
			if(p2>=0.5)
				predictionGrid[classIndex*numOfClasses+2]++;
			else
				predictionGrid[classIndex*numOfClasses+3]++;		
		}
		
		skipLine (fp);
		
		ret = fscanf(fp, "%s", tstring);
	}
	
	return NULL;
}

void RSDNeuralNetwork_test (RSDNeuralNetwork_t * RSDNeuralNetwork, RSDCommandLine_t * RSDCommandLine, FILE * fpOut)
{
	if(RSDNeuralNetwork==NULL)
		return;
		
	if(RSDCommandLine->opCode!=OP_TEST_CNN)
		return;
		
	assert(RSDCommandLine!=NULL);
	assert(fpOut!=NULL);
	
	fprintf(fpOut, "\n");
	fprintf(stdout, "\n");
	
	char tstring[STRING_SIZE], testCommand[STRING_SIZE], tstringF[STRING_SIZE], runNameSanitized[STRING_SIZE/2];
	int i=-1, j=-1, k=-1;	
	
	if(RSDCommandLine->numberOfClasses!=RSDNeuralNetwork->classSize)
	{
		fprintf(fpOut, "\nERROR: Class size mismatch between the command line (-clp %d) and the trained model (class size %d)!\n\n", RSDCommandLine->numberOfClasses, 
																	     RSDNeuralNetwork->classSize);
																	  
		fprintf(stderr, "\nERROR: Class size mismatch between the command line (-clp %d) and the trained model (class size %d)!\n\n", RSDCommandLine->numberOfClasses, 
																	      RSDNeuralNetwork->classSize);

		fclose(fpOut);
		exit(1);
	}
	
	for(i=0;i<RSDCommandLine->numberOfClasses;i++)
	{
		int match = 0;
		for(j=0;j<RSDNeuralNetwork->classSize;j++)
		{
			if(!strcmp(RSDCommandLine->classLabelList[i], RSDNeuralNetwork->classLabel[j]))
			{
				match = 1;
				
				strcpy(tstring, RSDCommandLine->classPathList[i]);
				
				strcpy(RSDCommandLine->classPathList[i], RSDCommandLine->inputFileName);
				strcat(RSDCommandLine->classPathList[i],"/");
				strcat(RSDCommandLine->classPathList[i], tstring);
						
				break;
			}
		}
		
		if(match==0)
		{
			fprintf(fpOut, "\nERROR: Class label %s (provided through -clp) not supported by the trained model (see %s/classLabels.txt)!\n\n",  RSDCommandLine->classLabelList[i], 
												       							    RSDNeuralNetwork->modelPath);
			fprintf(stderr, "\nERROR: Class label %s (provided through -clp) not supported by the trained model (see %s/classLabels.txt)!\n\n", RSDCommandLine->classLabelList[i], 
												       							    RSDNeuralNetwork->modelPath);

			fclose(fpOut);			
			exit(1);
		}
	}
	
	if(!strcmp(RSDCommandLine->networkArchitecture, ARC_FASTER_NN_G))
	{
		fprintf(fpOut, " Testing model %s (%s, groups=%d) using directory %s\n\n", RSDNeuralNetwork->modelPath, RSDNeuralNetwork->networkArchitecture, RSDCommandLine->fasterNNgroups, RSDCommandLine->inputFileName);
		fprintf(stdout, " Testing model %s (%s, groups=%d) using directory %s\n\n", RSDNeuralNetwork->modelPath, RSDNeuralNetwork->networkArchitecture, RSDCommandLine->fasterNNgroups, RSDCommandLine->inputFileName);
	}
	else
	{
		fprintf(fpOut, " Testing model %s (%s) using directory %s\n\n", RSDNeuralNetwork->modelPath, RSDNeuralNetwork->networkArchitecture, RSDCommandLine->inputFileName);
		fprintf(stdout, " Testing model %s (%s) using directory %s\n\n", RSDNeuralNetwork->modelPath, RSDNeuralNetwork->networkArchitecture, RSDCommandLine->inputFileName);
	}
	
	int * predictionGrid = (int*)rsd_malloc(sizeof(int)*RSDCommandLine->numberOfClasses*RSDCommandLine->numberOfClasses);
	assert(predictionGrid!=NULL);
	
	int maxClassLabelLength = 0;
	for(i=0;i<RSDNeuralNetwork->classSize;i++)
		maxClassLabelLength = (int)strlen(RSDNeuralNetwork->classLabel[i])>maxClassLabelLength?(int)strlen(RSDNeuralNetwork->classLabel[i]):maxClassLabelLength;
		
	int maxClassPathLength = 0;
	for(i=0;i<RSDNeuralNetwork->classSize;i++)
		maxClassPathLength = (int)strlen(RSDCommandLine->classPathList[i])>maxClassPathLength?(int)strlen(RSDCommandLine->classPathList[i]):maxClassPathLength;	
	
	for(i=0;i<RSDNeuralNetwork->classSize;i++)
	{
		for(k=0;k<RSDCommandLine->numberOfClasses;k++)
			if(!strcmp(RSDCommandLine->classLabelList[k],RSDNeuralNetwork->classLabel[i]))
				break;
				
		assert(k>=0);
		assert(k<RSDCommandLine->numberOfClasses);		
			
		RSDNeuralNetwork_createRunCommand (RSDNeuralNetwork, RSDCommandLine, RSDCommandLine->classPathList[k], testCommand);
		
		//fprintf(fpOut, " %d: Python-cmd: %s\n", i, testCommand);
		//fprintf(stdout, " %d: Python-cmd: %s\n", i, testCommand);		
		
		exec_command (testCommand);
		
		for(j=0;j<RSDCommandLine->numberOfClasses;j++)
			predictionGrid[i*RSDCommandLine->numberOfClasses+j]=0;
			
		
		sanitizeString(RSDCommandLine->runName, runNameSanitized, STRING_SIZE/2);	
		snprintf(tstringF, STRING_SIZE, "tempOutputFolder-%s-rsdai/PredResults.txt", runNameSanitized);	
		FILE * fp = fopen(tstringF, "r");
		assert(fp!=NULL);
		
		RSDNeuralNetwork_readPredictionFile (RSDNeuralNetwork, fp, i, RSDCommandLine->numberOfClasses, predictionGrid); 		
		fclose(fp);

		snprintf(tstringF, STRING_SIZE, "rm -r tempOutputFolder-%s-rsdai", runNameSanitized);
		exec_command (tstringF);
	}
	
	int samplesStrLen = 2;
	
	for(i=0;i<RSDNeuralNetwork->classSize;i++) 
	{		
		int sum = 0; 		
		for(j=0;j<RSDCommandLine->numberOfClasses;j++)
			sum+=predictionGrid[i*RSDCommandLine->numberOfClasses+j];			
			
		sum = sum / (RSDCommandLine->numberOfClasses/2); // div by 2 due to binary classification
			
		sprintf(tstring, "%d", sum);		
		samplesStrLen = (int)strlen(tstring)>samplesStrLen?(int)strlen(tstring):samplesStrLen;
		
		for(k=0;k<RSDCommandLine->numberOfClasses;k++)
			if(!strcmp(RSDCommandLine->classLabelList[k],RSDNeuralNetwork->classLabel[i]))
				break;
				
		assert(k>=0);
		assert(k<RSDCommandLine->numberOfClasses);
		
		fprintf(fpOut, " True class: %-*s | Test data: %-*s  (%*d samples/images) | Predicted class:",  maxClassLabelLength, RSDNeuralNetwork->classLabel[i], 
													 	maxClassPathLength, RSDCommandLine->classPathList[k], 
													 	samplesStrLen, sum);
													 	
		fprintf(stdout, " True class: %-*s | Test data: %-*s (%*d samples/images) | Predicted class:", 	maxClassLabelLength, RSDNeuralNetwork->classLabel[i], 
													 	maxClassPathLength, RSDCommandLine->classPathList[k], 
													 	samplesStrLen, sum);		
		
		for(j=0;j<RSDNeuralNetwork->classSize-1;j++)
		{
			fprintf(fpOut, " %*d %s -", samplesStrLen, predictionGrid[i*RSDNeuralNetwork->classSize+j], RSDNeuralNetwork->classLabel[j]);
			fprintf(stdout, " %*d %s -", samplesStrLen, predictionGrid[i*RSDNeuralNetwork->classSize+j], RSDNeuralNetwork->classLabel[j]);		
		}

		fprintf(fpOut, " %*d %s \n", samplesStrLen, predictionGrid[i*RSDNeuralNetwork->classSize+j], RSDNeuralNetwork->classLabel[j]);
		fprintf(stdout, " %*d %s \n", samplesStrLen, predictionGrid[i*RSDNeuralNetwork->classSize+j], RSDNeuralNetwork->classLabel[j]);				
	}
	
	fprintf(fpOut, "\n");
	fprintf(stdout, "\n");
	
	int slen = 20 + maxClassLabelLength;
	
	float * precisionPerClass = (float*)rsd_malloc(sizeof(float)*RSDNeuralNetwork->classSize);
	assert(precisionPerClass!=NULL);
	
	for(i=0;i<RSDNeuralNetwork->classSize;i++)
	{
		float precisionNom = predictionGrid[i*RSDCommandLine->numberOfClasses+i], precisionDenom = 0.0;
		
		for(j=0;j<RSDNeuralNetwork->classSize;j++)
			precisionDenom+=(float)predictionGrid[j*RSDCommandLine->numberOfClasses+i];
			
		precisionPerClass[i] = (precisionNom/precisionDenom)*100.0;
		
		strcpy(tstring, "Precision for class ");
		strcat(tstring, RSDNeuralNetwork->classLabel[i]);
		
		fprintf(fpOut, " %-*s  :\t%*.3f %%\n", slen, tstring, 8, precisionPerClass[i]);
		fprintf(stdout, " %-*s  :\t%*.3f %%\n", slen, tstring, 8, precisionPerClass[i]);	
	}
	
	fprintf(fpOut, "\n");
	fprintf(stdout, "\n");
	
	float * recallPerClass = (float*)rsd_malloc(sizeof(float)*RSDNeuralNetwork->classSize);
	assert(recallPerClass!=NULL);
	
	for(i=0;i<RSDNeuralNetwork->classSize;i++)
	{
		float recallNom = predictionGrid[i*RSDCommandLine->numberOfClasses+i], recallDenom = 0.0;
		
		for(j=0;j<RSDCommandLine->numberOfClasses;j++)
			recallDenom+=(float)predictionGrid[i*RSDCommandLine->numberOfClasses+j];
		
		recallPerClass[i] = (recallNom/recallDenom)*100.0;
		
		strcpy(tstring, "Recall for class ");
		strcat(tstring, RSDNeuralNetwork->classLabel[i]);
			
		fprintf(fpOut, " %-*s  :\t%*.3f %%\n", slen, tstring, 8, recallPerClass[i]);
		fprintf(stdout, " %-*s  :\t%*.3f %%\n", slen, tstring, 8, recallPerClass[i]);	
	}
	
	fprintf(fpOut, "\n");
	fprintf(stdout, "\n");
	
	for(i=0;i<RSDNeuralNetwork->classSize;i++)
	{
		float f1_score = 2.0*(precisionPerClass[i]*recallPerClass[i])/(precisionPerClass[i]+recallPerClass[i]);
		
		strcpy(tstring, "F1-score for class ");
		strcat(tstring, RSDNeuralNetwork->classLabel[i]);
			
		fprintf(fpOut, " %-*s  :\t%*.3f %%\n", slen, tstring, 8, f1_score);
		fprintf(stdout, " %-*s  :\t%*.3f %%\n", slen, tstring, 8, f1_score);	
	}

	fprintf(fpOut, "\n");
	fprintf(stdout, "\n");
	
	float accuracyNom = 0.0, accuracyDenom = 0.0;
	
	for(i=0;i<RSDNeuralNetwork->classSize;i++)
	{
		accuracyNom += predictionGrid[i*RSDCommandLine->numberOfClasses+i];
		
		for(j=0;j<RSDCommandLine->numberOfClasses;j++)
			accuracyDenom+=(float)predictionGrid[i*RSDCommandLine->numberOfClasses+j];
	}
	
	fprintf(fpOut, " %-*s  :\t%*.3f %%\n", slen, "Accuracy", 8, (accuracyNom/accuracyDenom)*100.0);
	fprintf(stdout, " %-*s  :\t%*.3f %%\n", slen, "Accuracy", 8, (accuracyNom/accuracyDenom)*100.0);		
	
	free(predictionGrid);
	free(precisionPerClass);
	free(recallPerClass);			
}

void RSDNeuralNetwork_printPackageDependency (char * dependency, FILE * fpOut)
{
	assert(dependency!=NULL);
	assert(fpOut!=NULL);
	
	fprintf(fpOut, " %s:\t", dependency);
	fprintf(stdout, " %s:\t", dependency);
	
	char tstring[STRING_SIZE];	
	strncpy(tstring, "pip3 show ", STRING_SIZE);
	strcat(tstring, dependency);

	FILE * fp = popen(tstring, "r");
	assert(fp!=NULL);
	
	int rcnt = fscanf(fp, "%s", tstring);
	assert(rcnt==1);
	
	rcnt = fscanf(fp, "%s", tstring);
	assert(rcnt==1);
	
	fprintf(fpOut, "%s", tstring); // name
	fprintf(stdout, "%s", tstring); // name
	
	rcnt = fscanf(fp, "%s", tstring);
	assert(rcnt==1);
	
	rcnt = fscanf(fp, "%s", tstring);
	assert(rcnt==1);
	
	fprintf(fpOut, " %s\n", tstring); // version
	fprintf(stdout, " %s\n", tstring); // version
	
	int c=0;
	while ((c = fgetc(fp)) != EOF);
	
	pclose(fp);
	
	fflush(fpOut);
	fflush(stdout);	
}

void randomPermutation(const char *iString, char *oString) 
{
	assert(iString!=NULL);
	assert(oString!=NULL);
	
	size_t len = strlen(iString);

	/* copy input into output */
	strcpy(oString, iString);

	for (size_t i = len - 1; i > 0; i--) 
	{
		size_t j = rand() % (i + 1);

		char tmp = oString[i];
		oString[i] = oString[j];
		oString[j] = tmp;
	}
}

void RSDNeuralNetwork_printPythonVersion (FILE * fpOut)
{
	assert(fpOut!=NULL);

	fprintf(fpOut, " Python\t\t     :\t");
	fprintf(stdout, " Python\t\t     :\t");

	FILE *fp = popen("python3 --version", "r");
	
	assert(fp!=NULL);
	
	char tchar = (char)fgetc(fp);	

	while(tchar!=EOF)
	{
		fprintf(fpOut, "%c", tchar);
		fprintf(stdout, "%c", tchar);
		
		tchar = (char)fgetc(fp);
	}

	pclose(fp);
		
	fflush(fpOut);
	fflush(stdout);
}

void RSDNeuralNetwork_printDependencies (RSDCommandLine_t * RSDCommandLine, FILE * fpOut)
{
	assert(RSDCommandLine!=NULL);
	assert(fpOut!=NULL);
	
	if(RSDCommandLine->opCode != OP_TRAIN_CNN && RSDCommandLine->opCode != OP_TEST_CNN && RSDCommandLine->opCode != OP_USE_CNN)
		return;
		
	RSDNeuralNetwork_printPythonVersion (fpOut);
		
	if(RSDCommandLine->enTF==1)	
	{		
		RSDNeuralNetwork_printPackageDependency ("Tensorflow          ", fpOut);	
		RSDNeuralNetwork_printPackageDependency ("Keras               ", fpOut);
		RSDNeuralNetwork_printPackageDependency ("Pillow              ", fpOut);
		RSDNeuralNetwork_printPackageDependency ("Matplotlib          ", fpOut);
		RSDNeuralNetwork_printPackageDependency ("H5PY                ", fpOut);
	}
	else
	{
		RSDNeuralNetwork_printPackageDependency ("torch               ", fpOut);
		RSDNeuralNetwork_printPackageDependency ("torchvision         ", fpOut);
	}	
}

void RSDNeuralNetwork_getColumnHeaders 	(RSDNeuralNetwork_t * RSDNeuralNetwork, RSDCommandLine_t * RSDCommandLine, char * colHeader1, char * colHeader2)
{
	assert(RSDNeuralNetwork!=NULL);
	assert(RSDCommandLine!=NULL);
	assert(colHeader1!=NULL);
	assert(colHeader2!=NULL);

	if(RSDCommandLine->classification2x2En==1 && !strcmp(RSDCommandLine->networkArchitecture, ARC_SWEEPNETRECOMB))
	{
		//strcpy(colHeader1, RSDNeuralNetwork->classLabel[RSDCommandLine->positiveClassIndex[0]]);
		//strcpy(colHeader2, RSDNeuralNetwork->classLabel[RSDCommandLine->positiveClassIndex[1]]);
		
		strcpy(colHeader1, RSDNeuralNetwork->cl4_1x_label);
		strcpy(colHeader2, RSDNeuralNetwork->cl4_x1_label);	
	}
	else
	{
		strcpy(colHeader1, RSDNeuralNetwork->classLabel[RSDCommandLine->positiveClassIndex[0]]);
		strcpy(colHeader2, "muvar^");
		strcat(colHeader2, RSDNeuralNetwork->classLabel[RSDCommandLine->positiveClassIndex[0]]);
	}
}
#endif
