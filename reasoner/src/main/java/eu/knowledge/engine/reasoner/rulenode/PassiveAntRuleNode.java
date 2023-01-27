package eu.knowledge.engine.reasoner.rulenode;

import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Future;

import eu.knowledge.engine.reasoner.BaseRule;
import eu.knowledge.engine.reasoner.api.BindingSet;
import eu.knowledge.engine.reasoner.api.TripleVarBindingSet;

/**
 * 
 * Passive means that it cannot be applied.
 * 
 * @author nouwtb
 *
 */
public class PassiveAntRuleNode extends AntRuleNode {

	public PassiveAntRuleNode(BaseRule aRule) {
		super(aRule);
	}

	public void setFilterBindingSetOutput(BindingSet bs) {
		this.filterBindingSetOutput = new TripleVarBindingSet(this.getRule().getAntecedent(), bs);
	}

	@Override
	public boolean readyForTransformFilter() {
		return false;
	}

	@Override
	public void transformFilterBS() {
		assert false;
	}

	@Override
	public boolean readyForApplyRule() {
		return false;
	}

	@Override
	public Future<Void> applyRule() {
		assert false;
		CompletableFuture<Void> f = new CompletableFuture<>();
		f.completeExceptionally(new IllegalStateException("`applyRule` cannot be called for PassiveAntRuleNodes."));
		return f;
	}
}