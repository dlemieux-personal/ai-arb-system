class RiskLearner:

    def learn_risk(self, pattern, risk):

        query = """
        MATCH (p:ArchitecturePattern {signature:$pattern})
        MERGE (r:Risk {name:$risk})
        MERGE (p)-[:INTRODUCES_RISK]->(r)
        """

        self.graph.run(query)