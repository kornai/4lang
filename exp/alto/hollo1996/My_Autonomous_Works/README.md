# NLP-Graph-transformation

##ALTO console usage
###Use this command:java -cp <path to ALTO's jar> de.up.ling.irtg.script.ParsingEvaluator <path to inputfile> -g <path to one of the irtg's> -I tree
###not perfect
###forExample:java -cp "/home/hollo/BMENotes/6.felev_4,83_37/Önlab(5)/alto-2.2-SNAPSHOT-jar-with-dependencies.jar" de.up.ling.irtg.script.ParsingEvaluator input_example_1 -g "NewSolution_(stable).irtg" -I tree

## OldSolution.irtg
### date-of-creation:2018.05.20
### discription: This is my old solution for the task. It uses tree and graph languages. Parses grammer tree to dependency graph. I already understand the concept and most of the format. I could make the verb independent in the tree language, but I did not find the right format for the graph language.
### usage: Use the well known grammer tree of "john loves mary" in the well known format: S(NP(NN(john)),VP(V(loves),NP(NN(mary))))

## NewSolution2.0_Stable.irtg
### date-of-creation:2018.07.03
### discription: This is my new Stable solution for the task. We did not understand the tricks of tag tree grammer at one point, so it uses graph algebra twice and tag tree algebra once. Parses sintactic tree to dependency graph. I already understand the concept and I understand both algebra, and both concepts. I made the words perfectly independen, and the structure very dinamic and modular, but the best solution is used only in my teamworks.
### usage: Use the well known grammer tree of "john loves mary" in the well known format: S(NP2(DT(this),NN(item)),VP(VBZ(is)),UCP(NP3(DT(a),JJ(small),CD(one)),CC(and),VP2(ADVP(RB(easily)),VBN(missed))))

## NewSolution2.0_UnderTesting.irtg
### date-of-creation:2018.07.08
### discription: It is the same as NewSolution2.0_Stable.irtg except some features and other impruvements under.
### usage: Use the well known grammer tree of "john loves mary" in the well known format: S(NP2(DT(this),NN(item)),VP(VBZ(is)),UCP(NP3(DT(a),JJ(small),CD(one)),CC(and),VP2(ADVP(RB(easily)),VBN(missed))))

## partTexter.irtg
### date-of-creation:2018.07.03
### discription: It is an irtg created to test only the newest features, algebras, and the wierd things of ALTO.
### usage: Don't Use.

## input_example_1
### date-of-creation:2018.07.08
### discription: It is an inutfile example for my new solution. It can be used for console testing of the NewSolution2.0_Stable.irtg.

## Data_for_next_mission
### date-of-creation:2018.07.03
### discription: It contains many information about the last implemented example.
