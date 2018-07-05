# NLP-Graph-transformation
##ALTO usage
###Unfortunatel the documents on ALTO's bitbucket do not contain information about any console version but you can run the gui with the "java -jar alto-2.2-SNAPSHOT-jar-with-dependencies.jar" command from the right folder. Here you can go to File/load irtg. After you chose one of the files under, you can chose Tools/Parse and input any tree in the given format. After this you just have to press Tools/Show Language. If it is not Choseable, you has made mistake in the format or semantics or you just has over estimated the state of the developement.
## OldSolution.irtg
### date-of-creation:2018.05.20
### discription: This is my old solution for the task. It uses tree and graph languages. Parses grammer tree to dependency graph. I already understand the concept and most of the format. I could make the verb independent in the tree language, but I did not find the right format for the graph language.
### usage: Use the well known grammer tree of "john loves mary" in the well known format: S(NP(NN(john)),VP(V(loves),NP(NN(mary))))
## NewSolution.irtg
### date-of-creation:2018.07.03
### discription: This is my new solution for the task. It uses tree and graph languages. Parses grammer tree to dependency graph. I already understand the concept and I'am not far from understanding even the graph format. I made the words perfectly independen, however did not perfect it on the highest levels of the trees.
### usage: Use the well known grammer tree of "john loves mary" in the well known format: S(NP(NN(john)),VP(V(loves),NP(NN(mary))))
