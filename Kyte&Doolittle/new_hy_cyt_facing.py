##################################################
#####      Converts .dat files to            #####
#####     ID, NAME, AVERAGE KD, KD profile.  #####
#####   The rightmost number of the profile  #####
#####   is at the cytosolic edge of the TMD. #####
#####        Script by James Baker           #####
#####       University of Manchester         #####
##################################################

#requires PYTHON3
#requires KD_calc.pl in the working directory

import os
import subprocess
import re

#This requires a working version of Biopython and numpy.
#SeqIO is a biopython module that can automatically parse uniprot .txt files
from Bio import SeqIO
import numpy

### BIOPYTHON STANDARD VARIABLES FOR SEQ-IO ###

#These are the variables that are repeatedly used throughout the script.

filenames = ["input/bsubtilis168.txt"] ##########CHANGE THIS TO "YOUR.dat" FILE############



input_format = "swiss" #This works with uniprot filetype
feature_type = "TRANSMEM" #This is the TM helix. http://www.uniprot.org/help/transmem
other_feature_type = "TOPO_DOM" #This is a domain that has topology.http://www.uniprot.org/help/topo_dom

### PULLING EACH ENTRY FROM THE .DAT FILE. ###

big_list_of_direction_helices = []
for filename in filenames:
    for record in SeqIO.parse(filename, input_format):
        this_id_record = []




        ### TOPOLOGY CHECKER ###
        #We are only interested in finding helices with annotated cytoplasmic regions.
        #This opens the loop within the record (ie loops through the features in a single id)
        for i, f in enumerate(record.features):

            #if the feature is a TRANSMEM region then...
            if f.type == feature_type:



                if i+1 < len(record.features):
                    next_feature = record.features[i+1]
                    previous_feature = record.features[i-1]


                    #This checks that the record has topological domain annotation.
                    if next_feature.type == other_feature_type:





                        ###Cytoplasmic facing###
                        #Checks that the next feature is a cytoplasmic region
                        if "Cytoplasmic" in str(next_feature.qualifiers):

                            #This checks that the cytoplasmic region starts where the transmembrane sequence ends.Be wary that location uses python slicing and zero-base counting rather than human friendly couting. https://www.biostars.org/p/139981/#140157
                            if f.location.end == next_feature.location.start:

                                #This fetches the sequence from the record according to the transmem annotation. This corrects the zero-base counting and python slicing of the location.
                                cyt_facing_TMD = f.extract(record.seq)


                                ### DO THING HERE ###

                                # Kyte & Doolittle index of hydrophobicity - Jim Warwickers' script uses the same scale.
                                kd = {'A': 1.8, 'R':-4.5, 'N':-3.5, 'D':-3.5, 'C': 2.5, 'Q':-3.5, 'E':-3.5, 'G':-0.4, 'H':-3.2, 'I': 4.5, 'L': 3.8,'K':-3.9, 'M':1.9, 'F': 2.8, 'P':-1.6,'S':-0.8, 'T':-0.7, 'W':-0.9, 'Y':-1.3, 'V': 4.2}

                                TMD = list(cyt_facing_TMD)

                                TMD_KD_complete = []

                                for i in TMD:
                                    hydrophobicity = kd[i]
                                    TMD_KD_complete.append(hydrophobicity)


                                TMD_KD_avg = numpy.mean(TMD_KD_complete)



                                #Extract human readable name of ID
                                protein_name = record.description
                                start_name = protein_name.find("Full=")
                                end_name = protein_name.find(";")
                                protein_name = protein_name[start_name+5:end_name]
                                protein_name = protein_name.replace(',','-')



                                # HYDROPATHY with Jims script
                                for x in TMD:
                                    with open('KD_calc_in.txt','w') as temp_fasta:
                                        temp_fasta.write(">")
                                        temp_fasta.write(protein_name)
                                        temp_fasta.write("\n")
                                        temp_fasta.write(str(cyt_facing_TMD))


                                var = "/"
                                pipe = subprocess.Popen(["perl", "KD_calc.pl", var])
                                pipe.wait()


                                with open('KDcalc_out.txt', 'r') as totalKD:
                                    lines = totalKD.readlines()

                                    KD_line = lines[4]
                                    totalKD.close()
                                os.remove("KDcalc_out.txt")
                                os.remove("KD_calc_in.txt")
                                KD_line = str(KD_line[4:])


                                KD_line =KD_line.replace('  ', ' ')
                                KD_line =KD_line.replace(' ', ',')


                                print(record.id, ",", protein_name,",", TMD_KD_avg,",", KD_line)





                        ### not cytoplasmic facing, these TRANSMEM sequences should be reversed - still unsure of what to do for Plasma membrane... ###

                        elif "Cytoplasmic" in str(previous_feature.qualifiers):

                            #This checks that the next topological domain starts where the transmembrane sequence ends.
                            if f.location.start == previous_feature.location.end:

                                non_cyt_facing_TMD = f.extract(record.seq)
                                non_cyt_facing_TMD = non_cyt_facing_TMD[::-1]

                                #DO THING HERE
                                # Kyte & Doolittle index of hydrophobicity
                                kd = {'A': 1.8, 'R':-4.5, 'N':-3.5, 'D':-3.5, 'C': 2.5, 'Q':-3.5, 'E':-3.5, 'G':-0.4, 'H':-3.2, 'I': 4.5, 'L': 3.8,'K':-3.9, 'M':1.9, 'F': 2.8, 'P':-1.6,'S':-0.8, 'T':-0.7, 'W':-0.9, 'Y':-1.3, 'V': 4.2}

                                TMD = list(non_cyt_facing_TMD)

                                TMD_KD_complete = []

                                for i in TMD:
                                    hydrophobicity = kd[i]
                                    TMD_KD_complete.append(hydrophobicity)
                                    TMD_KD_avg = numpy.mean(TMD_KD_complete)

                                #Extract human readable name of ID
                                protein_name = record.description
                                start_name = protein_name.find("Full=")
                                end_name = protein_name.find(";")
                                protein_name = protein_name[start_name+5:end_name]
                                protein_name = protein_name.replace(',','-')



                                # HYDROPATHY with Jims script
                                for y in TMD:
                                    with open('KD_calc_in.txt','w') as temp_fasta:
                                        temp_fasta.write(">")
                                        temp_fasta.write(protein_name)
                                        temp_fasta.write("\n")
                                        temp_fasta.write(str(non_cyt_facing_TMD))


                                var = "/"
                                pipe = subprocess.Popen(["perl", "KD_calc.pl", var])
                                pipe.wait()


                                with open('KDcalc_out.txt', 'r') as totalKD:
                                    lines = totalKD.readlines()
                                    KD_line = lines[4]
                                    totalKD.close()
                                os.remove("KDcalc_out.txt")
                                os.remove("KD_calc_in.txt")
                                KD_line = str(KD_line[4:])

                                KD_line =KD_line.replace('  ', ' ')
                                KD_line =KD_line.replace(' ', ',')

                                print(record.id, ",", protein_name,",", TMD_KD_avg,",", KD_line)


print("End.")
