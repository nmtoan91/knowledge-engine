package eu.interconnectproject.knowledge_engine.reasonerprototype;

import java.net.URI;
import java.util.List;

import eu.interconnectproject.knowledge_engine.reasonerprototype.api.TriplePattern;

public class RemoteRule extends Rule {

	private final URI knowledgeInteractionId;

	public RemoteRule(List<TriplePattern> lhs, List<TriplePattern> rhs, URI knowledgeInteractionId) {
		super(lhs, rhs);
		this.knowledgeInteractionId = knowledgeInteractionId;
	}

	public URI getKnowledgeInteractionId() {
		return knowledgeInteractionId;
	}

}
