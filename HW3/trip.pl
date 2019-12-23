totalcost(X):-
	findall(packages(O,P),offer(O,P,A,U),TotalPackagesWithD),
	compress(TotalPackagesWithD,TotalPackages),
	combinelist(TotalPackages,TotalCombine),
	%writeln(TotalCombine),

	calAllCost(TotalCombine,AllCost),
	%writeln(AllCost),
	list_min(AllCost,X),
	item_at(Index,AllCost,X),
	%writeln(Index),
	item_at(Index,TotalCombine,ChoosenCombine),
	%writeln(ChoosenCombine),
	write('Accepted offers:'),
	printResult(ChoosenCombine).

printResult([]).
printResult([packages(O,P)|T]):-
	write(' package '),
	write(P),
	write(' of tour operator '),
	write(O),
	write(','),
	printResult(T).

comb(_,[]).
comb([X|T],[X|Comb]):-comb(T,Comb).
comb([_|T],[X|Comb]):-comb(T,[X|Comb]).

combinelist(TotalPackages,Listlist):-
	findall(X,
		%meet maxacceptedoffer
		(comb(TotalPackages,X),
		extract(X,TotalO),
		encodeNum(TotalO,Temp),
		maxlist(Temp,MaxLen),
		maxacceptedoffer(K),
		MaxLen=<K,
		findall([A,U],need(A,U),TotalNeed),
		
		calNeed(X,ChoosenNeed),
		decode(ChoosenNeed,ChoosenNeedDecode),
		quicksort(ChoosenNeedDecode,SortedChoosenNeedDecode),
		encode(SortedChoosenNeedDecode,SortedChoosenNeed),
		judgeNeed(TotalNeed,SortedChoosenNeed)
		),Listlist).

item_at( N, L, Item ) :-
    item_at( N, 0, L, Item ).   
item_at( N, Count, [H|_], Item ) :-
    CountNew is Count + 1,
    CountNew = N,
    Item = H.
item_at( N, Count, [_|T], Item ) :-
    CountNew is Count + 1,
    item_at( N, CountNew, T, Item ).

calAllCost([],[]).
calAllCost([ChoosenPackages|T1],[HCost|T2]):-
	%writeln(ChoosenPackages),
	calCost(ChoosenPackages,HCost),
	calAllCost(T1,T2).

calCost([],0).
calCost([packages(O,P)|TChoosenPackages],Cost):-
	calCost(TChoosenPackages,Total),
	price(O,P,C),
	Cost is Total+C.

judgeEach([A1,U1],[]):- fail.
judgeEach([A1,U1],[[A1,U2]|T]):-
	U1 =< U2,!,true.
judgeEach([A1,U1],[[A2,U2]|T]):-
	judgeEach([A1,U1],T).

judgeNeed([],SortedChoosenNeed).
judgeNeed([H|T],SortedChoosenNeed):-
	judgeEach(H,SortedChoosenNeed),
	judgeNeed(T,SortedChoosenNeed).

calNeed([],[]).
calNeed([packages(O,P)|TPackages],ChoosenNeed):-
	calNeed(TPackages,SubNeed),
	findall([A,U],offer(O,P,A,U),EachNeed),
	%writeln(EachNeed),
	append(EachNeed,SubNeed,ChoosenNeed).

extract([],[]).
extract([packages(O,P)|Tail],[O|Tail1]):-
	extract(Tail,Tail1).

list_min([L|Ls], Min) :-
    list_min(Ls, L, Min).

list_min([], Min, Min).
list_min([L|Ls], Min0, Min) :-
    Min1 is min(L, Min0),
    list_min(Ls, Min1, Min).

maxlist([],0).
maxlist([Head|Tail],Max) :-
    maxlist(Tail,TailMax),
    Head > TailMax,
    Max is Head.
maxlist([Head|Tail],Max) :-
    maxlist(Tail,TailMax),
    Head =< TailMax,
    Max is TailMax.

pack([],[]).
pack([X|Xs],[Z|Zs]) :- transfer(X,Xs,Ys,Z), pack(Ys,Zs).
length([],0).
length([_|L],N) :- length(L,N1), N is N1 + 1.

encode(L1,L2) :- pack(L1,L), transform(L,L2).
transform([],[]).
transform([[X|Xs]|Ys],[[X,N]|Zs]) :- length([X|Xs],N), transform(Ys,Zs).

transfer(X,[],[],[X]).
transfer(X,[Y|Ys],[Y|Ys],[X]) :- X \= Y.
transfer(X,[X|Xs],Ys,[X|Zs]) :- transfer(X,Xs,Ys,Zs).

encodeNum(L1,L2) :- pack(L1,L), transformNum(L,L2).
transformNum([],[]).
transformNum([[X|Xs]|Ys],[N|Zs]) :- length([X|Xs],N), transformNum(Ys,Zs).

quicksort([], []).
quicksort([X0|Xs], Ys) :-
	partition(X0, Xs, Ls, Gs),
	quicksort(Ls, Ys1),
	quicksort(Gs, Ys2),
	append(Ys1, [X0|Ys2], Ys).
partition(Pivot,[],[],[]).
partition(Pivot,[X|Xs],[X|Ys],Zs) :-
	X =< Pivot,
	!, % cut
	partition(Pivot,Xs,Ys,Zs).
partition(Pivot,[X|Xs],Ys,[X|Zs]) :-
	partition(Pivot,Xs,Ys,Zs).

delete(X, [X|Ys], Ys).
delete(X, [Y|Ys], [Y|Zs]) :-
	delete(X, Ys, Zs).
	
decode([],[]).
decode([X|Ys],[X|Zs]) :- \+ is_list(X), decode(Ys,Zs).
decode([[X,1]|Ys],[X|Zs]) :- decode(Ys,Zs).
decode([[X,N]|Ys],[X|Zs]) :- N > 1, N1 is N - 1, decode([[X,N1]|Ys],Zs).

append([],A,A).
append([X|A],B,[X|C]):-
	append(A,B,C).

compress([],[]).
compress([X],[X]).
compress([X,X|Xs],Zs) :- compress([X|Xs],Zs).
compress([X,Y|Ys],[X|Zs]) :- X \= Y, compress([Y|Ys],Zs).