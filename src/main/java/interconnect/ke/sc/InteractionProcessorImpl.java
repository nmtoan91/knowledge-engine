package interconnect.ke.sc;

import java.net.URI;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.concurrent.CompletableFuture;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import interconnect.ke.api.AskResult;
import interconnect.ke.api.RecipientSelector;
import interconnect.ke.api.binding.BindingSet;
import interconnect.ke.api.interaction.AnswerKnowledgeInteraction;
import interconnect.ke.api.interaction.AskKnowledgeInteraction;
import interconnect.ke.api.interaction.KnowledgeInteraction;
import interconnect.ke.messaging.AnswerMessage;
import interconnect.ke.messaging.AskMessage;
import interconnect.ke.messaging.MessageDispatcherEndpoint;
import interconnect.ke.messaging.PostMessage;
import interconnect.ke.messaging.ReactMessage;

public class InteractionProcessorImpl implements InteractionProcessor {

	private static final Logger LOG = LoggerFactory.getLogger(InteractionProcessorImpl.class);

	private final OtherKnowledgeBaseStore otherKnowledgeBaseStore;
	private MessageRouter messageRouter;
	private MyKnowledgeBaseStore myKnowledgeBaseStore;
	private MetaKnowledgeBase myMetaKnowledgeBase;

	public InteractionProcessorImpl(OtherKnowledgeBaseStore otherKnowledgeBaseStore) {
		super();
		this.otherKnowledgeBaseStore = otherKnowledgeBaseStore;
	}

	@Override
	public CompletableFuture<AskResult> processAskFromKnowledgeBase(AskKnowledgeInteraction anAKI,
			RecipientSelector aSelector, BindingSet aBindingSet) {

		assert anAKI != null : "the knowledge interaction should be non-null";
		assert aBindingSet != null : "the binding set should be non-null";

		// TODO use RecipientSelector. In the MVP we interpret the recipient selector as
		// a wildcard.

		// retrieve other knowledge bases
		Set<OtherKnowledgeBase> otherKnowledgeBases = otherKnowledgeBaseStore.getOtherKnowledgeBases();
		Set<KnowledgeInteraction> otherKnowledgeInteractions = new HashSet<KnowledgeInteraction>();

		for (OtherKnowledgeBase otherKB : otherKnowledgeBases) {
			otherKnowledgeInteractions.addAll(otherKB.getKnowledgeInteractions());
		}

		// create a new SingleInteractionProcessor to handle this ask.
		SingleInteractionProcessor processor = new SerialMatchingProcessor(otherKnowledgeInteractions,
				this.messageRouter);

		// give the caller something to chew on while it waits. This method starts the
		// interaction process as far as it can until it is blocked because it waits for
		// outstanding message replies. Then it returns the future. Threads from the
		// MessageDispatcher will finish this process and the thread that handles the
		// last reply message will complete the future and notify the caller
		// KnowledgeBase.
		CompletableFuture<AskResult> future = processor.processInteraction(anAKI, aBindingSet);

		return future;
	}

	@Override
	public CompletableFuture<AnswerMessage> processAskFromMessageRouter(AskMessage anAskMsg) {
		URI answerKnowledgeInteractionId = anAskMsg.getToKnowledgeInteraction();
		AnswerKnowledgeInteraction answerKnowledgeInteraction;
		try {
			answerKnowledgeInteraction = (AnswerKnowledgeInteraction) myKnowledgeBaseStore
					.getKnowledgeInteractionById(answerKnowledgeInteractionId).getKnowledgeInteraction();
		} catch (Throwable t) {
			LOG.warn("Encountered an unresolvable KnowledgeInteraction ID '" + answerKnowledgeInteractionId
					+ "' that was expected to resolve to one of our own.");
			var future = new CompletableFuture<AnswerMessage>();
			future.completeExceptionally(t);
			return future;
		}

		var future = new CompletableFuture<AnswerMessage>();
		{
			BindingSet bindings = null;
			if (answerKnowledgeInteraction.getIsMeta()) {
				// TODO: Ask MyMetaKnowledgeBase for the bindings.
			} else {
				var handler = myKnowledgeBaseStore.getAnswerHandler(answerKnowledgeInteractionId);
				// TODO This should happen in the single thread for the knowledge base
				bindings = handler.answer(answerKnowledgeInteraction, anAskMsg.getBindings());
			}

			AnswerMessage result = new AnswerMessage(anAskMsg.getToKnowledgeBase(), answerKnowledgeInteractionId,
					anAskMsg.getFromKnowledgeBase(), anAskMsg.getFromKnowledgeInteraction(), anAskMsg.getMessageId(),
					bindings);
			// TODO: Here I just complete the future in the same thread, but we should
			// figure out how to do it asynchronously.
			future.complete(result);
		}
		return future;
	}

	@Override
	public CompletableFuture<ReactMessage> processPostFromMessageRouter(PostMessage aPostMsg) {
		// TODO Implement after MVP phase.
		return null;
	}

	@Override
	public void setMessageRouter(MessageRouter messageRouter) {
		this.messageRouter = messageRouter;
	}

	@Override
	public void unsetMessageRouter() {
		this.messageRouter = null;
	}

}