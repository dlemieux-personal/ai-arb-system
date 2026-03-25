class OutcomeLearner:

    def record_outcome(self, submission_id, outcome):

        query = """
        MATCH (s:ArchitectureSubmission {id:$id})
        MERGE (o:ArchitectureOutcome {type:$outcome})
        MERGE (s)-[:RESULTED_IN]->(o)
        """

        self.graph.run(query)