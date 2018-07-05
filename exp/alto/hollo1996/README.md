# NLP-Graph-transformation

##ALTO console usage
###Use this command:java -cp <path to ALTO's jar> de.up.ling.irtg.script.ParsingEvaluator <path to inputfile> -g <path to one of the irtg's> -I tree
###not perfect
###forExample:java -cp "/home/hollo/BMENotes/6.felev_4,83_37/Önlab(5)/alto-2.2-SNAPSHOT-jar-with-dependencies.jar" de.up.ling.irtg.script.ParsingEvaluator input_example_1 -g NewSolution.irtg -I tree

## OldSolution.irtg
### date-of-creation:2018.05.20
### discription: This is my old solution for the task. It uses tree and graph languages. Parses grammer tree to dependency graph. I already understand the concept and most of the format. I could make the verb independent in the tree language, but I did not find the right format for the graph language.
### usage: Use the well known grammer tree of "john loves mary" in the well known format: S(NP(NN(john)),VP(V(loves),NP(NN(mary))))
## NewSolution.irtg
### date-of-creation:2018.07.03
### discription: This is my new solution for the task. It uses tree and graph languages. Parses grammer tree to dependency graph. I already understand the concept and I'am not far from understanding even the graph format. I made the words perfectly independen, however did not perfect it on the highest levels of the trees.
### usage: Use the well known grammer tree of "john loves mary" in the well known format: S(NP(NN(john)),VP(V(loves),NP(NN(mary))))
