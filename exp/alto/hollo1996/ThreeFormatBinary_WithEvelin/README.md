# ThreeFormatBinary_WithEvelin
##discription: This is an irtg group I am developping with many help from Evelin, who understands all of the linguistic background of the work. Her irtg transformes most of the dependency graphs into a four lang graph correctly, but it has to be cleared from old mistakes, debuged and impruved until it is a dynamic, modular and transparent.

##ALTO console usage
## discription: ALTO is tricky to use, but we figured out, so here you are. We give an example for imput file too.
###Use this command:java -cp <path to ALTO's jar> de.up.ling.irtg.script.ParsingEvaluator <path to inputfile> -g <path to one of the irtg's> -I tree
###forExample:java -cp "/home/hollo/BMENotes/6.felev_4,83_37/Önlab(5)/alto-2.2-SNAPSHOT-jar-with-dependencies.jar" de.up.ling.irtg.script.ParsingEvaluator input_example_1 -g "NewSolution_(stable).irtg" -I tree

##TFB_Main
###discription: This is the place of the Main Solution. It is developed by every example. It is ready when all of Evelin's irtg-s are processed by us.
### TFB_Main.irtg
#### date-of-creation:2018.07.23
#### discription: This is the final solutions file. It contains only the three necessary algebras. A tag tree algebra for the sintactic tree, a graph algebra for the dependency graph and a graph algebra for the four lang graph. It implements only the stable version of the first example yet.
#### usage: Use this tree for example: NP2 (NP (NN (trouble)), PP (IN (for), NP2 (NNS (years), S2(VP (TO (to)), VP (VB (come))))))
### TFB_Main_Test.irtg
#### date-of-creation:2018.07.05
#### discription: It is the same as TFB_Main.irtg except some features and other impruvements. For example this is the file to make and teyt fixes.
#### usage: Use this tree for example: NP2 (NP (NN (trouble)), PP (IN (for), NP2 (NNS (years), S2(VP (TO (to)), VP (VB (come))))))
### TFB_Main_Data
#### date-of-creation:2018.07.03
#### discription: It contains many information about the last implemented example. For example trees that cover all features, and the head of the rules from Evelin's irtg, that are covered.

##TFB_Basic
###discription: This is the the first implementted example. It is Pritty special becouse it used 4 format instead of three. This was the stadium we figured out, how to merge our different views. It is made for the sentence part: "a small one"
### TFB_Basic.irtg
#### date-of-creation:2018.07.23
#### discription: This is the final solutions file. It contains all the four algebras. It implements the full pattern.
#### usage: Use this tree for example: NP2 (NP (NN (trouble)), PP (IN (for), NP2 (NNS (years), S2(VP (TO (to)), VP (VB (come))))))
### TFB_Basic_Test.irtg
#### date-of-creation:2018.07.05
#### discription: It is the same as TFB_Basic.irtg except some features and other impruvements. For example this is the file to make and teyt fixes.
#### usage: Use this tree for example: NP2 (NP (NN (trouble)), PP (IN (for), NP2 (NNS (years), S2(VP (TO (to)), VP (VB (come))))))
### TFB_Basic_Data
#### date-of-creation:2018.07.03
#### discription: It contains many information about the last implemented example. For example trees that cover all features, and the head of the rules from Evelins irtg, that are covered.

##TFB_Examples

###TFB_Cleric
####discription: This is the place of the irtg made for the sentence: "This Killing of a respected cleric will be cousing us trouble for years to come"
#### TFB_Main.irtg
##### date-of-creation:2018.07.23
##### discription: This is the stable version. It contains only the three necessary algebras. A tag tree algebra for the sintactic tree, a graph algebra for the dependency graph and a graph algebra for the four lang graph. It implements only the part "This Killing of a respected cleric" and "trouble for years to come" yet.
##### usage: Use this tree for example: NP2 (NP (NN (trouble)), PP (IN (for), NP2 (NNS (years), S2(VP (TO (to)), VP (VB (come))))))
#### TFB_Cleric_Test.irtg
##### date-of-creation:2018.07.05
##### discription: It is the same as TFB_Main.irtg except some features and other impruvements. For example this is the file to make and teyt fixes.
##### usage: Use this tree for example: NP2 (NP (NN (trouble)), PP (IN (for), NP2 (NNS (years), S2(VP (TO (to)), VP (VB (come))))))
#### TFB_Cleric_Data
##### date-of-creation:2018.07.03
##### discription: It contains many information about the last implemented example. For example trees that cover all features, the full tree, the full dependency tree, the full derivation tree and all the relevant rules from Evelin's irtg.

