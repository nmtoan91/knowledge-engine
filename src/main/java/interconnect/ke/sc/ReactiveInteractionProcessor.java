package interconnect.ke.sc;

import java.util.concurrent.CompletableFuture;

import interconnect.ke.messaging.AnswerMessage;
import interconnect.ke.messaging.AskMessage;
import interconnect.ke.messaging.PostMessage;
import interconnect.ke.messaging.ReactMessage;

/**
 * The {@link ReactiveInteractionProcessor} receives {@link AskMessage} and
 * {@link PostMessage} objects, and is responsible for processing these into
 * respectively {@link AnswerMessage} and {@link ReactMessage} objects.
 * 
 * For this, it needs to know which knowledge interactions are offered by the
 * knowledge base that this smart connector is attached to. For this, it uses
 * {@link MyKnowledgeBaseStore}, and also {@link MyMetaKnowledgeBase} for the
 * knowledge interactions about the metadata that all smart connectors
 * automatically offer.
 */
public interface ReactiveInteractionProcessor {
	/**
	 * Interprets the given {@link AskMessage} and returns an
	 * {@link AnswerMessage} by delegating the {@link BindingSet} to the correct
	 * {@link AnswerHandler}, OR to a handler in {@link MyMetaKnowledgeBase} if
	 * the incoming message asks for metadata about this knowledge base.
	 *
	 * @param anAskMsg The {@link AskMessage} that requires an answer.
	 * @return A future {@link AnswerMessage}.
	 */
	public CompletableFuture<AnswerMessage> processAsk(AskMessage anAskMsg);

	/**
	 * Interprets the given {@link PostMessage} and returns a {@link ReactMessage}
	 * by delegating the {@link BindingSet} to the correct {@link ReactHandler},
	 * OR to a handler in {@link OtherKnowledgeBaseStore} if it concerns metadata
	 * about other knowledge bases.
	 *
	 * @param aPostMsg The {@link PostMessage} that requires a reaction.
	 * @return A future {@link ReactMessage}.
	 */
	public CompletableFuture<ReactMessage> processPost(PostMessage aPostMsg);
}