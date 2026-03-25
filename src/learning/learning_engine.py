class ArchitectureLearningEngine:

    def __init__(self, graph_client):
        self.graph = graph_client

    def learn_from_review(self, submission, review_result):

        self.store_submission(submission)
        self.store_agent_findings(review_result)

        self.extract_patterns(submission)
        self.extract_risks(review_result)

    def store_submission(self, submission):

        query = """
        CREATE (s:ArchitectureSubmission {
            id: $id,
            title: $title,
            timestamp: datetime()
        })
        """

        self.graph.run(query, submission)

    def store_agent_findings(self, review):

        for finding in review["findings"]:
            query = """
            MATCH (s:ArchitectureSubmission {id:$submission_id})
            CREATE (f:AgentFinding {
                agent:$agent,
                severity:$severity,
                description:$description
            })
            CREATE (s)-[:HAS_FINDING]->(f)
            """

            self.graph.run(query, finding)