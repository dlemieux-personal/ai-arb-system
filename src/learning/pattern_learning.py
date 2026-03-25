class PatternLearner:

    def detect_pattern(self, submission):

        components = submission["components"]

        pattern_signature = "-".join(sorted(components))

        return pattern_signature

    def update_graph(self, graph, pattern):

        query = """
        MERGE (p:ArchitecturePattern {signature:$pattern})
        """

        graph.run(query, {"pattern": pattern})