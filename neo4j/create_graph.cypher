// Create nodes
USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'file:///graph_nodes.csv.gz' AS csvLine
    CREATE (:Malware {name:csvLine.node});

// Create index on the nodes
CREATE INDEX ON :Malware(name);

// Create relationships (neo4j only accepts directed relationships on create)
USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'file:///malware_names_graph.csv.gz' AS csvLine
    MATCH (a:Malware {name:csvLine.a})
    MATCH (b:Malware {name:csvLine.b})
    CREATE (a)-[:WEIGHT {weight:toInt(csvLine.weight)}]->(b);


// Get number of common nodes
MATCH (m1:Malware)-->(n:Malware)<--(m2:Malware) WHERE ID(m1) < ID(m2) RETURN m1, m2, COUNT(n) ORDER BY COUNT(n) DESC LIMIT 25;

MATCH (m1:Malware {name:'artemis'})--(n:Malware)--(m2:Malware) WHERE ID(m1) < ID(m2) AND n<>m1 AND n<>m2
MATCH (:Malware {name:m1.name})-[r:WEIGHT]->(:Malware {name:m1.name})
WITH m1, m2, r, COUNT(n) as n
RETURN m1, m2, r.weight, n, n/r.weight ORDER BY n DESC LIMIT 25;


MATCH (m1:Malware {name:'trojan'})--(n:Malware)--(m2:Malware) WHERE ID(m1) < ID(m2) AND n<>m1 AND n<>m2
MATCH (:Malware {name:m1.name})-[r:WEIGHT]->(:Malware {name:m1.name})
MATCH (:Malware {name:m2.name})-[r2:WEIGHT]->(:Malware {name:m2.name})
WITH m1, m2, r, r2, toFloat(COUNT(n)) as n, toFloat(COUNT(n))/r.weight as m1w, toFloat(COUNT(n))/r2.weight as m2w
RETURN m1, m2, r.weight, r2.weight, n, m1w, m2w ORDER BY n, m1w, m2w DESC LIMIT 25;


MATCH t=(:Malware {name:'trojan'})--(:Malware) WITH COUNT(t) AS t_freq
MATCH t2=(:Malware {name:'virus'})--(:Malware) WITH t_freq, COUNT(t2) AS v_freq
MATCH (m1:Malware {name:'trojan'})--(c1:Malware)--(m2:Malware) WITH t_freq, v_freq, COUNT(m2) AS m2_freq
MATCH (m3:Malware {name:'virus'})--(c2:Malware)--(m4:Malware) WHERE   ID(m1) < ID(m2) AND ID(m3) < ID(m4) AND m1<>c1 AND m2<>c1 AND m3<>c2 AND m4<>c2
RETURN m1, m2, m3, m4, t_freq, v_freq LIMIT 25;